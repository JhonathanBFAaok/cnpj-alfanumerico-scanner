using System;
using System.Text;
using System.Text.RegularExpressions;

/// <summary>
/// CNPJ alfanumerico - implementacao de referencia (IN RFB 2.229).
/// Validado contra 00.000.000/E08G-12, o primeiro emitido pela Receita em 31/07/2026.
///
/// Escrito em C# 5 / .NET Framework 4.0 de proposito: muita casa de software
/// brasileira ainda mantem sistema em versao antiga. Sem interpolacao de string,
/// sem LINQ, sem expression-bodied member.
/// </summary>
public static class CnpjAlfa
{
    private static readonly int[] Pesos = new int[] { 6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2 };
    private static readonly Regex Formato = new Regex("^[0-9A-Z]{12}[0-9]{2}$");
    private static readonly Regex Separadores = new Regex(@"[./-]");

    /// <summary>Remove SOMENTE os separadores. Nunca use \D aqui: isso apaga as letras.</summary>
    public static string Limpar(string cnpj)
    {
        if (cnpj == null) return string.Empty;
        return Separadores.Replace(cnpj, string.Empty).ToUpperInvariant();
    }

    private static int Digito(string baseStr)
    {
        int offset = Pesos.Length - baseStr.Length;
        int soma = 0;
        for (int i = 0; i < baseStr.Length; i++)
        {
            soma += ((int)baseStr[i] - 48) * Pesos[offset + i];   // 'A' = 17 ... 'Z' = 42
        }
        int resto = soma % 11;
        return resto < 2 ? 0 : 11 - resto;
    }

    public static string CalcularDv(string base12)
    {
        string b = Limpar(base12);
        if (b.Length > 12) b = b.Substring(0, 12);
        int d1 = Digito(b);
        int d2 = Digito(b + d1.ToString());
        return d1.ToString() + d2.ToString();
    }

    public static bool Validar(string cnpj)
    {
        string c = Limpar(cnpj);
        if (!Formato.IsMatch(c)) return false;

        bool todosIguais = true;
        for (int i = 1; i < c.Length; i++)
        {
            if (c[i] != c[0]) { todosIguais = false; break; }
        }
        if (todosIguais) return false;

        return CalcularDv(c.Substring(0, 12)) == c.Substring(12);
    }

    public static string Formatar(string cnpj)
    {
        string c = Limpar(cnpj);
        if (c.Length != 14) return cnpj;
        StringBuilder sb = new StringBuilder(18);
        sb.Append(c.Substring(0, 2)).Append('.')
          .Append(c.Substring(2, 3)).Append('.')
          .Append(c.Substring(5, 3)).Append('/')
          .Append(c.Substring(8, 4)).Append('-')
          .Append(c.Substring(12, 2));
        return sb.ToString();
    }
}
