// Original summaries linked to public sources; no copied artwork or bulk source text.
// This is reviewed retrieval, not a trained model. Unknown questions must fall through.
type Lang='pt'|'en'|'es';
const entries=[
  {
    "id": "condition",
    "reference": {
      "url": "https://help.tcgplayer.com/hc/en-us/articles/221430307-Card-Conditioning-Overview",
      "title": "TCGplayer — Card Conditioning"
    },
    "aliases": {
      "pt": [
        "condicao de uma carta",
        "estado de conservacao",
        "near mint",
        "nm",
        "lp",
        "mp",
        "hp",
        "dmg"
      ],
      "en": [
        "card condition",
        "near mint",
        "nm",
        "lp",
        "mp",
        "hp",
        "dmg"
      ],
      "es": [
        "estado de una carta",
        "near mint",
        "nm",
        "lp",
        "mp",
        "hp",
        "dmg"
      ]
    },
    "answers": {
      "pt": "Na escala de conservação do TCGplayer: NM (Near Mint) admite desgaste mínimo; LP, desgaste leve; MP, moderado; HP, acentuado; DMG, danificada. A classificação depende dos defeitos e da sua gravidade. É uma escala de condição física, não de raridade. Uma foto isolada não permite garantir a condição.",
      "en": "On TCGplayer’s condition scale: NM (Near Mint) allows minimal wear; LP means light wear; MP, moderate wear; HP, heavy wear; DMG, damaged. Classification depends on defects and their severity. This describes physical condition, not rarity. A single photo cannot guarantee condition.",
      "es": "En la escala de conservación de TCGplayer: NM (Near Mint) admite desgaste mínimo; LP, leve; MP, moderado; HP, intenso; DMG, dañada. La clasificación depende de los defectos y su gravedad. Describe el estado físico, no la rareza. Una sola foto no permite garantizar el estado."
    }
  },
  {
    "id": "mana",
    "reference": {
      "url": "https://magic.wizards.com/en/how-to-play",
      "title": "Wizards of the Coast — How to Play"
    },
    "aliases": {
      "pt": [
        "mana no magic",
        "mana em magic",
        "mana no mtg"
      ],
      "en": [
        "mana in magic",
        "mana in mtg"
      ],
      "es": [
        "mana en magic",
        "mana en mtg"
      ]
    },
    "answers": {
      "pt": "Em Magic: The Gathering, mana é um recurso usado para pagar custos de mágicas e habilidades. Terrenos são uma fonte comum de mana. Terreno e mana não são a mesma coisa: o terreno é a carta; a mana é o recurso produzido.",
      "en": "In Magic: The Gathering, mana is a resource used to pay spell and ability costs. Lands are a common source of mana. A land and mana are different: the land is the card; mana is the resource it produces.",
      "es": "En Magic: The Gathering, el maná es un recurso para pagar costes de hechizos y habilidades. Las tierras son una fuente habitual de maná. Tierra y maná son diferentes: la tierra es la carta; el maná es el recurso producido."
    }
  },
  {
    "id": "energy",
    "reference": {
      "url": "https://assets.pokemon.com/assets/cms2/pdf/trading-card-game/rulebook/par_rulebook_en.pdf",
      "title": "Pokémon — TCG Rulebook"
    },
    "aliases": {
      "pt": [
        "energia no pokemon",
        "energia no pokemon tcg",
        "uma carta de energia no pokemon"
      ],
      "en": [
        "energy in pokemon",
        "energy in pokemon tcg"
      ],
      "es": [
        "energia en pokemon",
        "energia en pokemon tcg"
      ]
    },
    "answers": {
      "pt": "No Pokémon TCG, Energias ligadas ao Pokémon atendem aos custos dos ataques. Compare os símbolos exigidos; um custo Incolor pode ser atendido por qualquer tipo de Energia. Efeitos específicos das cartas podem modificar as regras.",
      "en": "In Pokémon TCG, attached Energy meets attack costs. Match the required symbols; a Colorless cost accepts any Energy type. Specific card effects can change the rules.",
      "es": "En Pokémon TCG, las Energías unidas cumplen los costes de ataque. Comprueba los símbolos: un coste Incoloro acepta cualquier tipo de Energía. Los efectos específicos pueden modificar las reglas."
    }
  },
  {
    "id": "deck",
    "reference": {
      "url": "https://assets.pokemon.com/assets/cms2/pdf/trading-card-game/rulebook/par_rulebook_en.pdf",
      "title": "Pokémon — TCG Rulebook"
    },
    "aliases": {
      "pt": [
        "um deck no pokemon",
        "um baralho no pokemon",
        "um deck no pokemon tcg"
      ],
      "en": [
        "a deck in pokemon",
        "a deck in pokemon tcg"
      ],
      "es": [
        "un mazo en pokemon",
        "un mazo en pokemon tcg"
      ]
    },
    "answers": {
      "pt": "No jogo de mesa Pokémon TCG convencional, cada jogador usa um baralho de 60 cartas. Isso não descreve todos os modos especiais nem Pokémon TCG Pocket.",
      "en": "In conventional tabletop Pokémon TCG, each player uses a 60-card deck. This does not describe every special mode or Pokémon TCG Pocket.",
      "es": "En el Pokémon TCG de mesa convencional, cada jugador usa un mazo de 60 cartas. Esto no describe todos los modos especiales ni Pokémon TCG Pocket."
    }
  }
] as const;
const prefixes:Record<Lang,RegExp>={
 pt:/^(?:o que (?:e|significa)|explique|me explique|pode explicar) /,
 en:/^(?:what is|what does it mean|explain|please explain) /,
 es:/^(?:que (?:es|significa)|explica|explicame|puedes explicar) /
};
// Match complete definition requests, not arbitrary mentions of a condition.
// In particular HP with Pokémon context may mean hit points, not Heavily Played.
const conditionSubjects:Record<Lang,RegExp>={
 pt:/^(?:(?:uma? |a |o )?(?:carta|card|condicao|estado)(?: em| na condicao| no estado)? )?(near mint|nm|lp|mp|dmg)$/,
 en:/^(?:(?:an? |the )?(?:card|condition)(?: in)? )?(?:(?:an? |the )?)(near mint|nm|lp|mp|dmg)(?: card| condition)?$/,
 es:/^(?:(?:una? |la |el )?(?:carta|estado|condicion)(?: en| en estado)? )?(near mint|nm|lp|mp|dmg)$/
};
export function lookupAtlasGlossary(question:string,options:{hasAttachment?:boolean;cardId?:string}={}){
 if(options.hasAttachment||options.cardId||question.length>240)return null;
 const text=question.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim().replace(/^[¿¡]/,'').replace(/[?.!]+$/,'').trim().replace(/\s+/g,' ');
 for(const lang of ['pt','en','es'] as const){
  const englishMeaning=lang==='en'?text.match(/^what does (.+) mean$/):null;
  if(!prefixes[lang].test(text)&&!englishMeaning)continue;
  const subject=englishMeaning?englishMeaning[1]:text.replace(prefixes[lang],'');
  const condition=conditionSubjects[lang].exec(subject);
  const entry=entries.find(e=>e.id==='condition'&&condition||(e.aliases[lang] as readonly string[]).includes(subject));
  if(entry)return {answer:entry.answers[lang],source:'knowledge' as const,language:lang,
   sourceLabel:{pt:'Base revisada do Atlas · sem geração por IA',en:'Atlas reviewed knowledge · no AI generation',es:'Base revisada de Atlas · sin generación por IA'}[lang],
   references:[entry.reference],reviewedAt:'2026-11-19'};
 }
 return null;
}
