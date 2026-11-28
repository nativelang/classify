using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Text.Json;

namespace NativeLang.Classify;

/// <summary>Classifies requests locally. Reuse the instance and dispose it when finished.</summary>
public sealed class Classifier : IDisposable
{
    private readonly object gate = new();
    private Process? child;
    private bool closed;

    /// <summary>Returns an offered category, or null when the model abstains.</summary>
    public string? Classify(string text, params string[] categories)
    {
        lock (gate)
        {
            ObjectDisposedException.ThrowIf(closed, this);
            ArgumentNullException.ThrowIfNull(text);
            ArgumentNullException.ThrowIfNull(categories);
            string request = JsonSerializer.Serialize(new { text, categories });
            string? errorMessage;
            try
            {
                child ??= Start();
                child.StandardInput.WriteLine(request);
                child.StandardInput.Flush();
                var line = child.StandardOutput.ReadLine() ?? throw new IOException("Classify exited without returning a result");
                using var reply = JsonDocument.Parse(line);
                if (!reply.RootElement.TryGetProperty("error", out var error))
                    return reply.RootElement.GetProperty("status").GetString() switch
                    {
                        "matched" => reply.RootElement.GetProperty("category").GetString()
                            ?? throw new IOException("Missing matched category"),
                        "unknown" => null,
                        _ => throw new IOException("Unexpected Classify response")
                    };
                errorMessage = error.GetProperty("message").GetString();
            }
            catch (Exception failure)
            {
                try { DiscardWorker(); }
                catch (Exception cleanup) { failure.Data["ClassifyWorkerCleanup"] = cleanup; }
                throw;
            }
            // A well-formed request error leaves the worker ready for the next call.
            throw new IOException(errorMessage);
        }
    }

    private static Process Start()
    {
        bool windows = OperatingSystem.IsWindows();
        string name = windows ? "install.ps1" : "bootstrap.sh";
        using var resource = typeof(Classifier).Assembly.GetManifestResourceStream("NativeLang.Classify." + name)
            ?? throw new IOException("Classify package is missing " + name);
        using var reader = new StreamReader(resource, Encoding.UTF8);
        var info = new ProcessStartInfo("/bin/sh")
        {
            UseShellExecute = false,
            RedirectStandardInput = true,
            RedirectStandardOutput = true,
            StandardInputEncoding = new UTF8Encoding(false),
            StandardOutputEncoding = Encoding.UTF8
        };
        if (windows)
        {
            var shell = Path.Combine(Environment.SystemDirectory, "WindowsPowerShell", "v1.0", "powershell.exe");
            var install = new ProcessStartInfo(shell) { UseShellExecute = false, RedirectStandardInput = true, StandardInputEncoding = new UTF8Encoding(false), RedirectStandardOutput = true, StandardOutputEncoding = Encoding.UTF8 };
            foreach (var arg in new[] { "-NoProfile", "-NonInteractive", "-Command", "& ([ScriptBlock]::Create([Console]::In.ReadToEnd()))" })
                install.ArgumentList.Add(arg);
            using var proc = Process.Start(install) ?? throw new IOException("Could not install Classify");
            proc.StandardInput.Write(reader.ReadToEnd());
            proc.StandardInput.Close();
            var path = proc.StandardOutput.ReadToEnd().TrimEnd();
            proc.WaitForExit();
            if (proc.ExitCode != 0 || path.Length == 0) throw new IOException("Classify installation failed");
            info.FileName = path;
            info.ArgumentList.Add("infer");
            info.ArgumentList.Add("--profile");
            info.ArgumentList.Add(Path.Combine(Path.GetDirectoryName(path)!, "model", "profile.json"));
        }
        else
        {
            info.ArgumentList.Add("-c");
            info.ArgumentList.Add(reader.ReadToEnd());
        }
        return Process.Start(info) ?? throw new IOException("Could not start Classify");
    }

    private void DiscardWorker()
    {
        if (child is null) return;
        var worker = child;
        child = null;
        using (worker)
        using (worker.StandardOutput)
        using (worker.StandardInput)
        {
            if (!worker.HasExited)
            {
                worker.Kill(entireProcessTree: true);
                worker.WaitForExit();
            }
        }
    }

    public void Dispose()
    {
        lock (gate)
        {
            if (closed) return;
            closed = true;
            if (child is null) return;
            try
            {
                child.StandardInput.Close();
                if (!child.WaitForExit(5000))
                    throw new IOException("Classify did not shut down on EOF");
                if (child.ExitCode != 0) throw new IOException($"Classify exited with code {child.ExitCode}");
            }
            finally
            {
                DiscardWorker();
            }
        }
    }
}
