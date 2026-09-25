# Login e cadastro com Google (TEST)

O botão **Continuar com Google** usa o mesmo Supabase Auth do login por e-mail. No primeiro acesso, a conta passa pelo aceite obrigatório dos Termos e da Política de Privacidade antes de usar o app. O provedor deve entregar um e-mail confirmado. Contas com o mesmo e-mail confirmado podem ser vinculadas pelo Supabase Auth.

## Ativar em TEST

1. No Google Cloud Console, crie um cliente OAuth do tipo **Aplicativo da Web**, configure a tela de consentimento e adicione como URI de redirecionamento autorizado `https://hwsaxufycqgmzrxjxsfb.supabase.co/auth/v1/callback`.
2. No Supabase do projeto TEST (`hwsaxufycqgmzrxjxsfb`), em **Authentication → Providers → Google**, habilite Google e informe o Client ID e o Client Secret criados no Google. Não coloque o Client Secret no app nem no repositório.
3. Em **Authentication → URL Configuration**, inclua `https://cardcraftai-test.streamlit.app/?google_state=*` entre os Redirect URLs permitidos (ou uma regra equivalente para a URL pública do app). Confirme também a Site URL do projeto.
4. Nos Secrets do app Streamlit TEST, configure:

   ```toml
   GOOGLE_AUTH_ENABLED = "true"
   GOOGLE_APP_URL = "https://cardcraftai-test.streamlit.app"
   ```

5. Teste em navegador real um primeiro cadastro com Google, retorno ao app, aceite legal, login posterior, uma conta existente com e-mail confirmado e cancelamento do consentimento. Verifique se o e-mail e a conta são os esperados.

`GOOGLE_AUTH_ENABLED` começa desativado para que o botão só apareça depois de o provedor estar configurado. A URL pública é fixa e validada pelo servidor. Se o app passar a ter várias réplicas, o armazenamento temporário das tentativas OAuth deve passar do processo Streamlit para uma store compartilhada, preservando a vinculação ao navegador e o consumo único.
