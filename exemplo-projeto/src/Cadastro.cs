public class Empresa {
    public long Cnpj { get; set; }
    public bool ValidarCnpj(string cnpj) {
        cnpj = Regex.Replace(cnpj, @"\D", "");
        if (!long.TryParse(cnpj, out long numero)) return false;
        var doc = Convert.ToInt64(cnpj);
        return true;
    }
}
