# Validação da coleção

## Estado atual em 22/09/2026

Branch: `codex/cardcraftai-next`. A suíte local tem 19 testes passando. Os testes de interface usam cliente fictício em memória e não acessam Supabase.

O responsável pelo projeto confirmou nesta preparação que o ambiente `CardCraftAI-TEST` está criado e funcional e que as seguintes validações reais foram concluídas:

- Duas contas TESTE A e TESTE B validadas.
- TESTE A vê somente seu Pikachu; TESTE B vê somente seu Raichu.
- RLS validado para SELECT, UPDATE e DELETE entre contas.
- Organizar a coleção não consome créditos.
- Confirmação de e-mail, perfil inicial com 5 créditos e aceite legal validados.

Esses resultados foram informados pelo responsável, não reproduzidos pela suíte local. Nada foi aplicado em produção.

## Interface e testes locais

`Card language` e `Variant` usam seleções padronizadas e preservam valores antigos desconhecidos. `Other / Custom` permite variante personalizada. Limites mantidos: idioma 80 caracteres, variante 120, notas 2000 e quantidade de 0 a 9999.

Após atualização confirmada, o app exibe o toast `✅ Changes saved successfully.`, integrado ao sistema de traduções `t()`. O formulário permanece aberto. Durante a atualização, o botão fica desabilitado e mostra `Saving…`. Falhas preservam os valores digitados e permitem nova tentativa, sem expor detalhes técnicos. Resposta sem registro atualizado não gera confirmação de sucesso.

Os 19 testes cobrem validação, filtro de proprietário, exportações, proteção de notas privadas, fórmulas no Excel, filtros da interface, edição de idioma/variante/notas, valores legados, sucesso, falha, nova tentativa e tradução do feedback.

Instalar `requirements-dev.txt` e executar:

```text
python -B -m unittest discover -s tests -v
```

## Migration local e comparação com TEST

Arquivo: `supabase/migrations/20260918_collection_items.sql`.

A comparação entre a migration local e o banco `CardCraftAI-TEST` foi concluída e confirmada no TEST, conforme confirmação do responsável pelo projeto em 22/09/2026. Colunas, defaults, constraints e limites são equivalentes. A FK, o índice `collection_items_owner`, RLS, policies e privilégios abaixo também foram confirmados. Nada foi aplicado em produção.

| Item | Definição equivalente confirmada na migration local e no TEST |
| --- | --- |
| `id` | UUID, chave primária, default `gen_random_uuid()` |
| `user_id` | UUID NOT NULL, default `auth.uid()`; FK para `auth.users(id)` com `ON DELETE CASCADE` |
| `catalog_id`, `card_name` | TEXT NOT NULL, sem default; comprimento de 1 a 200 |
| `set_name`, `card_number`, `image_url` | TEXT NOT NULL, default string vazia |
| `quantity` | INTEGER NOT NULL, default 1; de 0 a 9999 |
| `condition` | TEXT NOT NULL, default `Not assessed`; opções abaixo |
| `language` | TEXT NOT NULL, default string vazia; até 80 caracteres |
| `variant` | TEXT NOT NULL, default string vazia; até 120 caracteres |
| `notes` | TEXT NOT NULL, default string vazia; até 2000 caracteres |
| `wishlist` | BOOLEAN NOT NULL, default false |
| `created_at` | TIMESTAMPTZ NOT NULL, default `now()` |
| Índice | `collection_items_owner` em `user_id` |
| RLS | Habilitado em `public.collection_items` |
| SELECT e DELETE | Políticas para `authenticated`, `USING (user_id = auth.uid())` |
| INSERT | Política para `authenticated`, `WITH CHECK (user_id = auth.uid())` |
| UPDATE | Política para `authenticated`, `USING` e `WITH CHECK (user_id = auth.uid())` |
| `anon` | Sem privilégios na tabela |
| `authenticated` | Somente SELECT, INSERT, UPDATE e DELETE |
| `service_role` | Somente SELECT, INSERT, UPDATE e DELETE |
| Privilégios removidos | TRUNCATE, REFERENCES e TRIGGER removidos de `authenticated` e `service_role` |

A configuração explícita revoga todos os privilégios de `anon`, `authenticated` e `service_role`, concedendo depois somente SELECT, INSERT, UPDATE e DELETE às duas últimas roles. As policies SELECT, INSERT, UPDATE e DELETE de `authenticated` restringem o proprietário por `user_id = auth.uid()`. Os grants de `service_role` não tornam essa role adequada para testar RLS.

Valores permitidos de `condition`: `Not assessed`, `Near Mint`, `Lightly Played`, `Moderately Played`, `Heavily Played`, `Damaged`.

Complementar a evidência funcional com INSERT em nome de outra conta, transferência de proprietário e acesso anônimo negados: esses casos não constam da confirmação atual de SELECT/UPDATE/DELETE. Validar RLS com sessões de usuários de teste, não com a chave `service_role`.

## Exportações e pendências

PDF e Excel foram inspecionados com dados fictícios, incluindo nomes e notas longos e acentos. PDF e Word são relatórios textuais; a exportação respeita filtros e inclui notas somente por opção explícita.

Word passou nos testes de geração e conteúdo, mas a revisão visual com LibreOffice permanece pendente. A cobertura de todos os alfabetos e símbolos do catálogo internacional não foi validada. Amostras e artefatos de QA não devem entrar no commit.

Antes de produção, revisar as demais pendências; a comparação do schema com TEST está concluída. Nenhuma migration é executada automaticamente pelo app e nada foi aplicado em produção.
