# MBC Fardamento - Gerador de Catálogos

Frontend para o sistema de geração automática de catálogos personalizados.

## Tecnologias

- React 18
- Vite
- Tailwind CSS
- Lucide React (ícones)

## Instalação

```bash
# Instalar dependências
npm install

# Copiar configuração
cp .env.example .env

# Editar .env com URL da API
```

## Desenvolvimento

```bash
# Iniciar servidor de desenvolvimento
npm run dev

# Abrir em http://localhost:3000
```

## Build para Produção

```bash
# Gerar build
npm run build

# Testar build localmente
npm run preview
```

## Estrutura

- `src/components/` - Componentes React
- `src/services/` - Serviços de API
- `src/utils/` - Funções auxiliares
- `public/` - Arquivos estáticos

## Features

- Upload de logótipo com preview
- Seleção dinâmica de artigos e cores (sincronizado com BD)
- 3 tipos de catálogo (Personalizado, Setor Padrão, Pack)
- Barra de progresso em tempo real
- Download automático do PDF

## Configuração

Editar `src/config.js` para alterar:
- URL da API
- Intervalo de polling
- Tamanho máximo do logótipo
- Timeout