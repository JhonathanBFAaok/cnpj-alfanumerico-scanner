<?php
/**
 * CNPJ alfanumerico - implementacao de referencia (IN RFB 2.229)
 * Validado contra 00.000.000/E08G-12 (primeiro emitido pela Receita em 31/07/2026)
 */
final class Cnpj
{
    private const PESOS = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];

    /** Remove SOMENTE os separadores. Nunca use \D aqui. */
    public static function limpar(?string $cnpj): string
    {
        return strtoupper(preg_replace('/[.\/-]/', '', (string) $cnpj));
    }

    private static function digito(string $base): int
    {
        $pesos = array_slice(self::PESOS, -strlen($base));
        $soma = 0;
        for ($i = 0; $i < strlen($base); $i++) {
            $soma += (ord($base[$i]) - 48) * $pesos[$i];   // 'A' = 17 ... 'Z' = 42
        }
        $resto = $soma % 11;
        return $resto < 2 ? 0 : 11 - $resto;
    }

    public static function calcularDv(string $base12): string
    {
        $base = substr(self::limpar($base12), 0, 12);
        $d1 = self::digito($base);
        $d2 = self::digito($base . $d1);
        return $d1 . $d2;
    }

    public static function validar(?string $cnpj): bool
    {
        $c = self::limpar($cnpj);
        if (!preg_match('/^[0-9A-Z]{12}[0-9]{2}$/', $c)) return false;
        if (count(array_unique(str_split($c))) === 1) return false;
        return self::calcularDv(substr($c, 0, 12)) === substr($c, 12);
    }

    public static function formatar(?string $cnpj): string
    {
        $c = self::limpar($cnpj);
        if (strlen($c) !== 14) return (string) $cnpj;
        return sprintf('%s.%s.%s/%s-%s',
            substr($c,0,2), substr($c,2,3), substr($c,5,3), substr($c,8,4), substr($c,12,2));
    }
}
