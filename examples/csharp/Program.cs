using System;
using NativeLang.Classify;

using var model = new Classifier();
string? category = model.Classify("This is a terrible movie", "positive", "negative", "neutral");
Console.WriteLine(category); // negative
