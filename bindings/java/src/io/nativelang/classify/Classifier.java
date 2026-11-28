package io.nativelang.classify;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Objects;
import java.util.concurrent.TimeUnit;

/** A local classifier. Reuse an instance for multiple requests and close it when done. */
public final class Classifier implements AutoCloseable {
    private record Request(String text, String[] categories) {}

    private static final Gson JSON = new Gson();
    private Process child;
    private BufferedWriter input;
    private BufferedReader output;
    private boolean closed;

    /** Returns an offered category, or null when the model abstains. */
    public synchronized String classify(String text, String... categories) throws IOException {
        if (closed) throw new IllegalStateException("Classifier is closed");
        Objects.requireNonNull(text, "text");
        Objects.requireNonNull(categories, "categories");
        String request = JSON.toJson(new Request(text, categories));
        String errorMessage;
        try {
            if (child == null) start();
            input.write(request);
            input.write('\n');
            input.flush();
            String line = output.readLine();
            if (line == null) throw new IOException("Classify exited without returning a result");
            JsonObject reply = JsonParser.parseString(line).getAsJsonObject();
            if (!reply.has("error")) {
                return switch (reply.get("status").getAsString()) {
                    case "matched" -> reply.get("category").getAsString();
                    case "unknown" -> null;
                    default -> throw new IOException("Unexpected Classify response");
                };
            }
            errorMessage = reply.getAsJsonObject("error").get("message").getAsString();
        } catch (IOException | RuntimeException e) {
            if (child != null) child.destroyForcibly();
            child = null;
            throw new IOException("Local Classify request failed", e);
        }
        // A well-formed request error leaves the worker ready for the next call.
        throw new IOException(errorMessage);
    }

    private void start() throws IOException {
        String script;
        try (InputStream resource = Classifier.class.getResourceAsStream("/io/nativelang/classify/bootstrap.sh")) {
            if (resource == null) throw new IOException("Classify package is missing bootstrap.sh");
            script = new String(resource.readAllBytes(), StandardCharsets.UTF_8);
        }
        child = new ProcessBuilder("/bin/sh", "-c", script)
                .redirectError(ProcessBuilder.Redirect.INHERIT).start();
        input = child.outputWriter(StandardCharsets.UTF_8);
        output = child.inputReader(StandardCharsets.UTF_8);
    }

    @Override
    public synchronized void close() throws IOException {
        if (closed) return;
        closed = true;
        if (child == null) return;
        try {
            input.close();
            if (!child.waitFor(5, TimeUnit.SECONDS)) {
                child.destroyForcibly().waitFor();
                throw new IOException("Classify did not shut down on EOF");
            }
            if (child.exitValue() != 0) throw new IOException("Classify exited with code " + child.exitValue());
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IOException("Interrupted while closing Classify", e);
        } finally {
            if (child.isAlive()) child.destroyForcibly();
            output.close();
        }
    }
}
