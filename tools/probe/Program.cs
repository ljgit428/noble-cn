using System.Reflection;
using System.Text;

var sb = new StringBuilder();
foreach (var dll in Directory.GetFiles(AppContext.BaseDirectory, "AssetsTools*.dll").OrderBy(x => x))
{
    var asm = Assembly.LoadFrom(dll);
    sb.AppendLine("##### ASSEMBLY " + asm.GetName().Name);
    foreach (var t in asm.GetExportedTypes().OrderBy(x => x.FullName))
    {
        if (!t.IsClass && !t.IsEnum && !t.IsInterface && !t.IsValueType) continue;
        sb.AppendLine("TYPE " + t.FullName + (t.IsEnum ? " (enum)" : ""));
        foreach (var c in t.GetConstructors())
            sb.AppendLine("   .ctor(" + string.Join(", ", c.GetParameters().Select(P)) + ")");
        foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly))
            sb.AppendLine("   " + (m.IsStatic ? "static " : "") + Short(m.ReturnType) + " " + m.Name + "(" + string.Join(", ", m.GetParameters().Select(P)) + ")");
        foreach (var f in t.GetFields(BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly))
            sb.AppendLine("   field " + Short(f.FieldType) + " " + f.Name);
    }
}
File.WriteAllText("api.txt", sb.ToString(), new UTF8Encoding(false));
Console.WriteLine("wrote api.txt " + sb.Length);
static string P(ParameterInfo p) => Short(p.ParameterType) + " " + p.Name + (p.HasDefaultValue ? " = " + (p.DefaultValue ?? "null") : "");
static string Short(Type t)
{
    if (t == null) return "?";
    if (t.IsGenericType) return t.Name.Split('`')[0] + "<" + string.Join(",", t.GetGenericArguments().Select(Short)) + ">";
    return t.Name;
}
