# Coleção pessoal — implantação

## Estado em 22/09/2026

Implementação na branch `codex/cardcraftai-next`, sem commit nesta preparação. A funcionalidade fica desativada quando `COLLECTIONS_ENABLED` não é configurada. Nada foi aplicado em produção.

O responsável pelo projeto confirmou que `CardCraftAI-TEST` está criado e funcional, com duas contas validadas: TESTE A vê somente seu Pikachu e TESTE B somente seu Raichu. SELECT, UPDATE e DELETE entre contas foram validados com RLS. Confirmação de e-mail, perfil inicial com 5 créditos e aceite legal também foram validados. Organizar a coleção não consome créditos.

A suíte local tem 19 testes passando, com dados fictícios. A comparação do banco `CardCraftAI-TEST` com `supabase/migrations/20260918_collection_items.sql` foi concluída e confirmada no TEST, conforme confirmação do responsável pelo projeto em 22/09/2026. Detalhes e demais pendências estão em [collection-validation.md](collection-validation.md).

Foram confirmados colunas e defaults equivalentes, constraints e limites equivalentes, FK `user_id -> auth.users(id) ON DELETE CASCADE`, índice `collection_items_owner` e RLS habilitado. As policies SELECT, INSERT, UPDATE e DELETE de `authenticated` restringem o acesso por `user_id = auth.uid()`. `anon` não possui privilégios; `authenticated` e `service_role` possuem somente SELECT, INSERT, UPDATE e DELETE. TRUNCATE, REFERENCES e TRIGGER foram removidos de ambas. Nada foi aplicado em produção.

## Funcionalidade entregue localmente

Cada inclusão cria um registro de exemplares, permitindo separar a mesma carta por idioma, variante ou condição. Quantidade zero com lista de desejos representa uma carta procurada. Não há botão de exclusão nesta etapa.

O álbum usa imagens do catálogo. A coleção oferece busca, filtros, lista de desejos, álbum/lista e exportações PDF, Word e Excel dos registros filtrados. Notas privadas só entram na exportação mediante opção explícita.

`Card language` e `Variant` usam seleções padronizadas e preservam valores antigos desconhecidos. `Other / Custom` permite variante personalizada. Os limites de idioma, variante, notas e quantidade permanecem iguais aos da migration.

O salvamento confirmado exibe o toast `✅ Changes saved successfully.` pelo sistema de traduções `t()`. O formulário permanece aberto. Durante o envio, `Saving…` indica processamento e o botão fica desabilitado. Em erro, os valores digitados são preservados e a mensagem não expõe detalhes técnicos.

A interface principal da coleção está em português/inglês; o feedback de salvamento tem traduções nos quatro idiomas do app. Cartas e notas são privadas. Perfis públicos e marketplace não fazem parte desta entrega e exigirão uma projeção própria que não exponha notas privadas.

## Preparação para produção

1. Comparação concluída: `supabase/migrations/20260918_collection_items.sql` corresponde ao schema validado no TEST, incluindo colunas/defaults, FK, constraints, índice, policies, RLS e grants. Usar essa migration na futura implantação autorizada.
2. Complementar o registro com INSERT em nome de outra conta, transferência de proprietário e acesso anônimo negados, ainda não confirmados no relato atual.
3. Concluir a revisão visual pendente de Word e avaliar a cobertura de caracteres internacionais nas exportações.
4. Após revisão e autorização de produção, aplicar a migration uma única vez ao ambiente correto, verificando antes se a tabela já existe. O arquivo usa `CREATE TABLE` e não é idempotente.
5. Habilitar `COLLECTIONS_ENABLED` em produção somente após validar a migration, as permissões e o isolamento naquele ambiente.

Nenhuma dessas ações de produção foi executada nesta preparação. Não copiar credenciais TEST para produção nem versionar Secrets.

## Verificação local e arquivos

Instalar `requirements-dev.txt` e executar:

```text
python -B -m unittest discover -s tests -v
```

A prévia `streamlit run prototypes/collection_preview.py` usa dados fictícios, não acessa Supabase e é utilizada pelos testes de interface. Deve acompanhar o código e os testes no commit.

Não incluir `.streamlit/secrets.toml`, caches Python, `tmp/`, `node_modules/`, exportações de QA ou a screenshot local. O `.gitignore` contém regras específicas; imagens legítimas não são ignoradas genericamente.
