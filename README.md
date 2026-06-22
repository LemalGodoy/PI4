# 🌍 PROJETO 17 — As ODS precisam de sua ajuda!

> Jogo de plataforma 2D educativo desenvolvido em Python com Pygame, abordando os **Objetivos de Desenvolvimento Sustentável (ODS)** da ONU.

---

## 📖 Sobre o Projeto

**PROJETO 17** é um jogo de plataforma 2D onde o jogador controla **Hope**, uma viajante planetária que aterrissa em um mundo devastado pelo vilão **Glitch**. O Glitch afetou 9 das 17 ODS e agora Hope precisa da sua ajuda para restaurá-las em uma trilha perigosa e desconhecida.

O jogo foi desenvolvido como **Projeto Integrador (PI)** com o objetivo de conscientizar os jogadores sobre os Objetivos de Desenvolvimento Sustentável da ONU de forma interativa e divertida.

---

## 🎮 Funcionalidades

- **Menu principal** animado com efeito de partículas e introdução narrativa estilo Star Wars
- **Lobby/Bazar** com mapa interativo — explore e acesse as fases disponíveis
- **5 fases jogáveis**, cada uma representando um ODS diferente:
  - ⚔️ **Fase 1 — Vitalidade** (cenário urbano/favela)
  - 🌊 **Fase 2 — A poluição já é visível...** (caverna/laboratório)
  - 🍽️ **Fase 3 — Situações Desiguais: Sede e Fome!** (indústria/poluição)
  - ⚡ **Fase 4 — Energia!** (sertão/seca)
  - 👁️ **Fase 5 — A verdade!** (boss fight final)
- **Sistema de progressão** — fases são desbloqueadas sequencialmente
- **Sistema de névoa** dinâmico que desaparece conforme o progresso
- **Boss fight** na fase final com mecânicas de dash, tiro e plataformas
- **Animações de sprites** completas (idle, corrida, pulo, tiro, dash)
- **Câmera dinâmica** com suavização e sistema de zoom

---

## 🕹️ Controles

| Ação | Tecla |
|------|-------|
| Mover | `W` `A` `S` `D` ou Setas direcionais |
| Pular | `W` / Seta para cima |
| Interagir / Entrar na fase | `E` ou `Enter` |
| Atirar (Boss Fight) | `F` |
| Dash (Boss Fight) | `Espaço` |
| Tela cheia | `F11` |
| Voltar / Sair | `ESC` |

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.13+**
- **Pygame 2.0+**
- **Pillow (PIL)** — para carregamento do GIF de loading

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.10 ou superior instalado
- pip (gerenciador de pacotes do Python)

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/LemalGodoy/PI4.git
   cd PI4
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute o jogo:
   ```bash
   python main.py
   ```

---

## 📁 Estrutura do Projeto

```
PI4/
├── assets/              # Sprites, imagens de fundo e assets visuais
│   ├── background.png   # Imagem de fundo do lobby
│   ├── iddle.png        # Spritesheet idle do personagem
│   ├── run.png          # Spritesheet de corrida
│   ├── jump.png         # Spritesheet de pulo
│   ├── shoot1/2.png     # Spritesheets de tiro
│   ├── nev1-4.png       # Camadas de névoa progressiva
│   ├── carimbo.png      # Carimbo de fase concluída
│   └── ...              # Demais assets do jogo
├── levels/              # Módulos das fases
│   ├── level_1.py       # Fase 1 — Vitalidade
│   ├── level_2.py       # Fase 2 — Poluição
│   ├── level_3.py       # Fase 3 — Fome e Sede
│   ├── level_4.py       # Fase 4 — Energia
│   └── level_5.py       # Fase 5 — Boss Fight Final
├── main.py              # Ponto de entrada, menu principal e loop do jogo
├── entities.py          # Classes do jogador, câmera, plataformas e armadilhas
├── lobby.py             # Cena do lobby/bazar com mapa interativo
├── renderer.py          # Funções auxiliares de renderização
├── camera.py            # Sistema de câmera
├── settings.py          # Configurações globais (resolução, assets, ODS)
├── utils.py             # Funções utilitárias
└── requirements.txt     # Dependências do projeto
```

---

## 👥 Equipe de Desenvolvimento

| Nome |
|------|
| Daniel Silva Souza |
| Franklin Pereira Santos Filho |
| Giovanni Turetta |
| Guilherme Gabriel Crispim |
| Kauã Gianei de Matos |
| Pedro Henrique Malpeli |

**PyGameLoaderFx:** kerodekroma

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos como parte do **Projeto Integrador (PI)**.

---

<p align="center">
  <i>Feito com ❤️ e Pygame</i>
</p>
