# Teste V0.2

## Home Assistant + bridge

1. `docker compose up -d homeassistant`
2. Abrir `http://127.0.0.1:8123` e concluir o onboarding.
3. Criar um Long-Lived Access Token em Home Assistant.
4. No shell: `export HA_TOKEN='...'`
5. `docker compose up -d bridge`
6. `curl http://127.0.0.1:8790/entities`
7. `curl http://127.0.0.1:8790/health`

O resultado deve conter apenas as entidades que o Home Assistant conhece e que o bridge suporta. A documentação oficial do Home Assistant expõe `/api/states` para estados atuais e WebSocket em `/api/websocket` para `get_states`, `get_services` e `state_changed`.

## Comando de teste

Depois de conferir o `entity_id` da luz:

```bash
curl -X POST http://127.0.0.1:8790/command \
  -H 'Content-Type: application/json' \
  -d '{"entity_id":"light.sala_light","action":"off"}'
```

Para a porta:

```bash
curl -X POST http://127.0.0.1:8790/command \
  -H 'Content-Type: application/json' \
  -d '{"entity_id":"cover.garagem_door","action":"open"}'
```

Os nomes exatos podem variar conforme o `entity_id` gerado pelo Home Assistant; use `/entities` como fonte de verdade.
