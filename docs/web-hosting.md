# Publicação da interface Next.js · CardCraftAI

Estado: código preparado na branch `staging`; a interface pública Next.js ainda não substitui o app Streamlit. Atlas, login, coleção, pagamentos e Shop continuam no app existente. Arena e game estão suspensos.

## Projeto de hospedagem (Vercel)

1. Importe o repositório `CardCraftIA/cardcraftai` em um projeto novo, inicialmente como **preview da branch `staging`**. Não substitua o domínio do Streamlit.
2. Selecione o framework **Next.js**, Root Directory **`web`** e Node.js **22**. O comando de instalação é `npm ci`; o build é `npm run build`. O script `prebuild` copia o índice público de `data/` para `web/data/` e valida seu formato.
3. Habilite **Include source files outside of the Root Directory in the Build Step**. Sem isso, o build em `web/` não consegue ler `../data/catalog_name_index_tcgdex_en.json`.
4. Configure `NEXT_PUBLIC_LEGACY_APP_URL=https://cardcraftai-test.streamlit.app` apenas no ambiente de preview. É um URL público, nunca uma chave secreta. O código possui esse URL de teste como fallback; configure explicitamente para evitar links para o ambiente errado.
5. Gere o preview, verifique a página inicial, busque `Pikachu` e confirme que Shop e Atlas abrem o app de teste. Confirme também que nenhum link para Arena ou game aparece na página.
6. Só depois de testar o preview, decida domínio e ambiente de produção. Para produção, configure o URL do app de produção; não use o endereço `-test` como destino definitivo.

O projeto usa a rota dinâmica `/api/catalog` e precisa de hospedagem com execução de Next.js/Node. Um export estático simples não atende à busca. A rota só lê o snapshot público de nomes, limitado a 24 resultados, e não usa credenciais do Supabase.

## Validação automatizada

O workflow `.github/workflows/tests.yml` agora instala dependências com `npm ci`, executa `npm run build` e faz um teste de fumaça HTTP da página e da busca. Localmente, a partir de `web/`, use os mesmos comandos. Publicações devem ocorrer após o workflow passar.

## Migração posterior

Esta publicação é uma entrada pública com navegação para o Streamlit. Login unificado e fluxos privados exigem API, controles de sessão, paridade funcional e testes de pagamento antes de migrar o domínio principal. Preserve a atual autenticação Google/redirect do Streamlit até essa etapa.
