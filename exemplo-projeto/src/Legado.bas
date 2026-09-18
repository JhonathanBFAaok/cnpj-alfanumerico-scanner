Attribute VB_Name = "modCadastro"
' Modulo legado de cadastro de fornecedor

Public Function ValidarCNPJ(ByVal sCnpj As String) As Boolean
    Dim lCnpj As Long
    lCnpj = Val(sCnpj)          ' converte o cnpj para numero
    If lCnpj = 0 Then
        ValidarCNPJ = False
        Exit Function
    End If
    ValidarCNPJ = True
End Function
