export const shopItems=[
{id:'pokemon-cards',name:'Cartas Pokémon',game:'Pokémon',group:'Cartas',query:'Pokémon TCG cards',icon:'✦'},
{id:'magic-cards',name:'Cartas Magic',game:'Magic',group:'Cartas',query:'Magic The Gathering cards',icon:'◈'},
{id:'yugioh-cards',name:'Cartas Yu-Gi-Oh!',game:'Yu-Gi-Oh!',group:'Cartas',query:'Yu-Gi-Oh cards',icon:'◇'},
{id:'onepiece-cards',name:'Cartas One Piece',game:'One Piece',group:'Cartas',query:'One Piece Card Game',icon:'⌁'},
{id:'pokemon-box',name:'Boosters Pokémon',game:'Pokémon',group:'Lacrados',query:'Pokemon TCG booster box',icon:'▣'},
{id:'magic-box',name:'Boosters Magic',game:'Magic',group:'Lacrados',query:'Magic The Gathering booster box',icon:'▣'},
{id:'sleeves',name:'Sleeves',game:'Todos',group:'Acessórios',query:'trading card sleeves',icon:'▱'},
{id:'binders',name:'Fichários',game:'Todos',group:'Acessórios',query:'trading card binder',icon:'▤'},
{id:'deckboxes',name:'Deck boxes',game:'Todos',group:'Acessórios',query:'trading card deck box',icon:'▧'},
{id:'toploaders',name:'Toploaders',game:'Todos',group:'Acessórios',query:'trading card top loaders',icon:'▯'}];
export function shopUrl(query:string,partner:string){return partner==='amazon'?'https://www.amazon.com.br/s?k='+encodeURIComponent(query):'https://www.tcgplayer.com/search/all/product?q='+encodeURIComponent(query);}
