using System;
using System.Linq;
using System.Text.RegularExpressions;

/// <summary>
/// CNPJ alfanumerico - implementacao de referencia (IN RFB 2.229).
/// Validado contra 00.000.000/E08G-12 (primeiro emitido pela Receita em 31/07/2026).
/// </summary>
public static class Cnpj
{
    private static readonly int[] Pesos = { 6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2 };
    private static readonly Regex Formato = new Regex("^[0-9A-Z]{12}[0-9]{2}$", RegexOptions.Compiled);
    private static readonly Regex Separadores = new Regex(@"[./-]", RegexOptions.Compiled);

    /// <summary>Remove SOMENTE os separadores. Nunca use \D aqui.</summary>
    public static string Limpar(string cnpj) =>
        Separadores.Replace(cnpj ?? string.Empty, string.Empty).ToUpperInvariant();

    private static int Digito(string baseStr)
    {
        var pesos = Pesos.Skip(Pesos.Length - baseStr.Length).ToArray();
        var soma = baseStr.Select((c, i) => ((int)c - 48) * pesos[i]).Sum();
        var resto = soma % 11;
        return resto < 2 ? 0 : 11 - resto;
    }

    public static string CalcularDv(string base12)
    {
        var b = Limpar(base12);
        if (b.Length > 12) b = b.Substring(0, 12);
        var d1 = Digito(b);
        var d2 = Digito(b + d1);
        return $"{d1}{d2}";
    }

    public static bool Validar(string cnpj)
    {
        var c = Limpar(cnpj);
        if (!Formato.IsMatch(c)) return false;
        if (c.Distinct().Count() == 1) return false;
        return CalcularDv(c.Substring(0, 12)) == c.Substring(12);
    }

    public static string Formatar(string cnpj)
    {
        var c = Limpar(cnpj);
        if (c.Length != 14) return cnpj;
        return $"{c.Substring(0,2)}.{c.Substring(2,3)}.{c.Substring(5,3)}/{c.Substring(8,4)}-{c.Substring(12,2)}";
    }
}
