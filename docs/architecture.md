# Arquitetura

O Home Assistant é a fonte de verdade. A primeira versão usa `GET /api/states` no bridge. A API WebSocket do Home Assistant oferece `get_states`, `get_services` e assinatura de `state_changed`; a V1 deve migrar para WebSocket para atualizar a interface por evento.

A ROM recebe `domain + features + state + name + value` e escolhe o renderer. Coordenadas X/Y existem somente como cálculo de layout, nunca como definição do dispositivo.
