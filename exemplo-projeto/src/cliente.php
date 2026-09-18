<?php
class ClienteController {
    public function salvar($dados) {
        $cnpj = preg_replace('/\D/', '', $dados['cnpj']);
        if (!is_numeric($cnpj)) {
            throw new Exception("CNPJ invalido");
        }
        $cnpjNumero = intval($cnpj);
        return $this->repo->inserir($cnpjNumero);
    }
    public function validarCNPJ($cnpj) {
        if (!preg_match('/^\d{14}$/', $cnpj)) return false;
        $soma = 0;
        for ($i = 0; $i < 12; $i++) {
            $soma += intval($cnpj[$i]) * $this->pesos[$i];
        }
        return true;
    }
}
