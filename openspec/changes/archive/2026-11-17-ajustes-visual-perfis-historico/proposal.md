# Proposal: Ajustes Visuais MonitoraUSID, Tela de Login Premium, Perfis Coerentes e Tela de Histórico

## Contexto e Motivação
Após a transição inicial da arquitetura base para o **MonitoraUSID**, faz-se necessária uma rodada de refinamentos visuais e funcionais para consolidar a identidade da aplicação e aprimorar a experiência do usuário (UX):
1. **Identidade Visual Unificada:** Padronizar o nome **"MonitoraUSID"** no título do documento (aba do navegador), no cabeçalho do layout e no rodapé da barra lateral.
2. **Tela de Login Premium:** Reformular o componente de Login (`Login.vue`) trazendo um visual moderno, glassmorphism e identidade corporativa do HC-UFPE/EBSERH.
3. **Perfis de Acesso Coerentes:** Ajustar os perfis de acesso RBAC no backend/frontend para alinhar com a operação de monitoramento: `ADMINISTRADOR` (gestão de aplicações e usuários), `OPERADOR` (reconhecimento de alertas e atualização de parâmetros) e `CONSULTA` (leitura dos dashboards).
4. **Simplificação de Menu:** Remover a opção "Exemplo" (menu genérico de cadastro de pacientes) mantendo o menu "Componentes" apenas para orientação visual dos desenvolvedores.
5. **Nova Tela de Histórico:** Criar um novo módulo e tela de **Histórico de Incidentes e Health Logs** (`/historico`), permitindo consultar o histórico de oscilações de latência, quedas e alertas do Zabbix por período.

## Objetivos Principais
- **Branding "MonitoraUSID":** Exibição correta na aba do navegador (`document.title`), topo da sidebar e rodapé.
- **Login Visualmente Impressionante:** Tela de autenticação moderna com background dinâmico, logo corporativo, feedback visual de erros e seleção entre AD Ebserh e Mock Local.
- **Perfis RBAC Alinhados:** Perfis `ADMINISTRADOR`, `OPERADOR` e `CONSULTA`.
- **Menu Limpo:** Substituição do menu "Exemplo" pelo menu "Histórico".
- **Visualização de Histórico:** Interface de tabela/filtros para consulta retroativa de instabilidade dos sistemas.
