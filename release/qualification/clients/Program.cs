using System;
using System.Linq;
using System.Runtime.InteropServices;
using NativeLang.Classify;

using var model = new Classifier();
Console.WriteLine(RuntimeInformation.ProcessArchitecture);
while (Console.ReadLine() is string line)
{
    var fields = line.Split('\t');
    Console.WriteLine(model.Classify(fields[0], fields.Skip(1).ToArray()));
}
