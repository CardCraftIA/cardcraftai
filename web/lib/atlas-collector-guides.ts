import {normalizeAtlasQuestion} from './atlas-question-intents.ts';
type Language='pt'|'en'|'es';
// Original short summaries. Source review is not a confirmation of a user's card.
const guides=[
  {
    "id": "storage",
    "references": [
      {
        "title": "Ultra PRO — Sleeves and Toploaders",
        "url": "https://ultrapro.com/blogs/news/a-top-to-bottom-guide-on-toploaders"
      }
    ],
    "terms": {
      "pt": [],
      "en": [],
      "es": []
    },
    "questions": {
      "pt": [
        "como guardar as cartas sem estragar",
        "como proteger minhas cartas",
        "como armazenar minhas cartas",
        "como conservar minhas cartas"
      ],
      "en": [
        "how should i store my cards",
        "how can i protect my cards"
      ],
      "es": [
        "como guardar mis cartas sin danarlas",
        "como proteger mis cartas"
      ]
    },
    "answers": {
      "pt": "Use sleeves do tamanho adequado e proteção externa compatível. Guarde em local seco, longe de luz intensa. Não force a carta no protetor; proteção reduz riscos, mas não garante conservação perfeita.",
      "en": "Use correctly sized sleeves and compatible outer protection. Store cards in a dry place away from harsh light. Never force a card into a holder; protection reduces risk, not all damage.",
      "es": "Usa fundas del tamaño adecuado y protección exterior compatible. Guarda las cartas en un lugar seco, lejos de luz intensa. No las fuerces dentro del protector; la protección reduce riesgos, no los elimina."
    }
  },
  {
    "id": "sleeves",
    "references": [
      {
        "title": "Ultra PRO — Sleeves and Toploaders",
        "url": "https://ultrapro.com/blogs/news/a-top-to-bottom-guide-on-toploaders"
      }
    ],
    "terms": {
      "pt": [
        "um sleeve",
        "um toploader"
      ],
      "en": [
        "a sleeve",
        "a toploader"
      ],
      "es": [
        "una funda",
        "un toploader"
      ]
    },
    "questions": {
      "pt": [
        "qual a diferenca entre sleeve e toploader",
        "preciso de sleeve dentro do toploader"
      ],
      "en": [
        "what is the difference between a sleeve and a toploader",
        "do i need a sleeve inside a toploader"
      ],
      "es": [
        "cual es la diferencia entre una funda y un toploader",
        "necesito una funda dentro del toploader"
      ]
    },
    "answers": {
      "pt": "O sleeve é uma capa fina e flexível; o toploader é um protetor externo mais rígido. Use a carta em sleeve antes de colocá-la no toploader, com tamanho e espessura compatíveis.",
      "en": "A sleeve is thin and flexible; a toploader is a stiffer outer holder. Sleeve the card before placing it in a toploader, using compatible dimensions and thickness.",
      "es": "La funda es fina y flexible; el toploader es un protector exterior más rígido. Coloca primero la carta en una funda y usa tamaños y grosores compatibles."
    }
  },
  {
    "id": "cleaning",
    "references": [
      {
        "title": "PSA — Grading Standards",
        "url": "https://www.psacard.com/gradingstandards"
      }
    ],
    "terms": {
      "pt": [],
      "en": [],
      "es": []
    },
    "questions": {
      "pt": [
        "posso limpar minha carta com alcool",
        "posso passar alcool na carta",
        "como limpar minhas cartas"
      ],
      "en": [
        "can i clean my card with alcohol",
        "how should i clean my cards"
      ],
      "es": [
        "puedo limpiar mi carta con alcohol",
        "como limpiar mis cartas"
      ]
    },
    "answers": {
      "pt": "Como precaução, não aplique álcool, solventes ou produtos de limpeza à carta. A PSA considera certas limpezas químicas uma alteração. Para sujeira persistente, procure orientação de conservação profissional antes de intervir.",
      "en": "As a precaution, do not apply alcohol, solvents or cleaning products to the card. PSA treats certain chemical cleaning as alteration. For persistent dirt, seek professional conservation advice before intervening.",
      "es": "Por precaución, no apliques alcohol, disolventes ni productos de limpieza a la carta. PSA considera ciertas limpiezas químicas una alteración. Ante suciedad persistente, busca asesoramiento profesional de conservación antes de intervenir."
    }
  },
  {
    "id": "grading",
    "references": [
      {
        "title": "PSA — Getting Started With Grading",
        "url": "https://www.psacard.com/info/get-started"
      }
    ],
    "terms": {
      "pt": [
        "grading",
        "graduacao de cartas",
        "uma carta graduada"
      ],
      "en": [
        "grading",
        "card grading",
        "a graded card"
      ],
      "es": [
        "grading",
        "la graduacion de cartas",
        "una carta graduada"
      ]
    },
    "questions": {
      "pt": [
        "como funciona a graduacao de cartas"
      ],
      "en": [
        "how does card grading work"
      ],
      "es": [
        "como funciona la graduacion de cartas"
      ]
    },
    "answers": {
      "pt": "Grading é a avaliação profissional do estado físico da carta. Superfície, cantos, bordas e centralização influenciam a nota. Autenticação é uma verificação distinta. O Atlas não emite nota certificada nem garante o resultado por foto.",
      "en": "Grading professionally evaluates a card’s physical condition. Surface, corners, edges and centering affect the grade. Authentication is a separate assessment. Atlas cannot issue a certified grade or guarantee a result from a photo.",
      "es": "El grading evalúa profesionalmente el estado físico de una carta. Superficie, esquinas, bordes y centrado influyen en la nota. La autenticación es una evaluación distinta. Atlas no certifica notas ni garantiza resultados mediante fotos."
    }
  },
  {
    "id": "grading-condition",
    "references": [
      {
        "title": "TCGplayer — Card Conditioning",
        "url": "https://help.tcgplayer.com/hc/en-us/articles/221430307-Card-Conditioning-Overview"
      },
      {
        "title": "PSA — Grading Standards",
        "url": "https://www.psacard.com/gradingstandards"
      }
    ],
    "terms": {
      "pt": [],
      "en": [],
      "es": []
    },
    "questions": {
      "pt": [
        "near mint e a mesma coisa que psa 10",
        "nm e psa 10",
        "uma carta near mint garante psa 10"
      ],
      "en": [
        "is near mint the same as psa 10",
        "does near mint guarantee psa 10"
      ],
      "es": [
        "near mint es lo mismo que psa 10",
        "una carta near mint garantiza psa 10"
      ]
    },
    "answers": {
      "pt": "Não. Near Mint é uma descrição de conservação que admite pequenas imperfeições. PSA 10 é uma nota específica, atribuída pela PSA após avaliação. Um anúncio NM não garante PSA 10.",
      "en": "No. Near Mint is a condition description allowing small imperfections. PSA 10 is a specific grade assigned by PSA after evaluation. An NM listing does not guarantee PSA 10.",
      "es": "No. Near Mint describe un estado que admite pequeñas imperfecciones. PSA 10 es una nota específica otorgada por PSA tras evaluar la carta. Un anuncio NM no garantiza PSA 10."
    }
  },
  {
    "id": "identify-set",
    "references": [
      {
        "title": "Pokémon — TCG Rulebook",
        "url": "https://assets.pokemon.com/assets/cms2/pdf/trading-card-game/rulebook/par_rulebook_en.pdf"
      }
    ],
    "terms": {
      "pt": [],
      "en": [],
      "es": []
    },
    "questions": {
      "pt": [
        "como descobrir a colecao da minha carta",
        "como identificar a colecao de uma carta pokemon",
        "como saber de qual colecao e minha carta pokemon"
      ],
      "en": [
        "how can i identify my pokemon card set",
        "how do i find the set of my pokemon card"
      ],
      "es": [
        "como identificar la coleccion de mi carta pokemon",
        "como saber de que coleccion es mi carta pokemon"
      ]
    },
    "answers": {
      "pt": "Para Pokémon, confira nome, número e símbolo ou código da coleção; compare no catálogo correspondente ao idioma. Mesma arte não basta para identificar a edição. Esta orientação não confirma sua carta.",
      "en": "For Pokémon, check the name, collector number and set symbol or code against the catalog for that language. Matching artwork alone does not identify an edition. This guidance does not confirm your card.",
      "es": "En Pokémon, compara nombre, número y símbolo o código de colección con el catálogo del idioma correspondiente. La misma ilustración no identifica por sí sola una edición. Esta orientación no confirma tu carta."
    }
  },
  {
    "id": "collector-number",
    "references": [
      {
        "title": "TCGplayer — Pokémon Card Numbers and Rarities",
        "url": "https://help.tcgplayer.com/hc/en-us/articles/360025636074-What-are-the-rarities-of-Pok%C3%A9mon-TCG-cards"
      }
    ],
    "terms": {
      "pt": [
        "o numero de colecionador no pokemon"
      ],
      "en": [
        "a pokemon collector number"
      ],
      "es": [
        "el numero de coleccionista en pokemon"
      ]
    },
    "questions": {
      "pt": [
        "o que significa o numero 123/100",
        "por que o numero da carta e maior que o total da colecao"
      ],
      "en": [
        "what does the number 123/100 mean",
        "why is the card number higher than the set total"
      ],
      "es": [
        "que significa el numero 123/100",
        "por que el numero de la carta es mayor que el total de la coleccion"
      ]
    },
    "answers": {
      "pt": "Em Pokémon, XXX/YYY costuma indicar o número da carta e o total anunciado da coleção. Em algumas coleções, cartas secretas são numeradas além desse total. O número sozinho não confirma coleção, raridade exata, autenticidade ou preço; confira a edição no catálogo.",
      "en": "In Pokémon, XXX/YYY usually indicates the card number and advertised set total. In some sets, secret cards are numbered beyond that total. The number alone does not confirm the set, exact rarity, authenticity or price; check the catalog edition.",
      "es": "En Pokémon, XXX/YYY suele indicar el número de carta y el total anunciado de la colección. En algunas colecciones, las cartas secretas se numeran más allá de ese total. El número solo no confirma colección, rareza exacta, autenticidad ni precio; consulta la edición."
    }
  },
  {
    "id": "promo",
    "references": [
      {
        "title": "PSA — Pokémon Collecting Basics",
        "url": "https://www.psacard.com/info/tcg/pokemon-basics-guide"
      }
    ],
    "terms": {
      "pt": [
        "uma carta promo",
        "uma carta promocional"
      ],
      "en": [
        "a promo card",
        "a promotional card"
      ],
      "es": [
        "una carta promo",
        "una carta promocional"
      ]
    },
    "questions": {
      "pt": [
        "o que significa promo no pokemon"
      ],
      "en": [
        "what does promo mean in pokemon"
      ],
      "es": [
        "que significa promo en pokemon"
      ]
    },
    "answers": {
      "pt": "No Pokémon TCG, cartas promocionais podem acompanhar produtos, eventos ou premiações. “Promo” descreve essa distribuição; não é uma garantia de valor. Confira a identificação da edição.",
      "en": "In Pokémon TCG, promotional cards may accompany products, events or prizes. “Promo” describes that distribution, not guaranteed value. Check the edition’s identifying details.",
      "es": "En Pokémon TCG, las cartas promocionales pueden acompañar productos, eventos o premios. “Promo” describe esa distribución, no garantiza valor. Comprueba los datos de la edición."
    }
  },
  {
    "id": "edition",
    "references": [
      {
        "title": "CGC — Pokémon First Editions",
        "url": "https://www.cgcgrading.com/news/articles/pokemon-first-editions-3RuIuDcH5mM8koeRHgmzrx/"
      },
      {
        "title": "PSA — Pokémon Collecting Basics",
        "url": "https://www.psacard.com/info/tcg/pokemon-basics-guide"
      }
    ],
    "terms": {
      "pt": [
        "uma reimpressao no pokemon"
      ],
      "en": [
        "a pokemon reprint"
      ],
      "es": [
        "una reimpresion en pokemon"
      ]
    },
    "questions": {
      "pt": [
        "qual a diferenca entre primeira edicao e reimpressao",
        "como reconhecer primeira edicao no pokemon"
      ],
      "en": [
        "what is the difference between first edition and a reprint",
        "how can i recognize first edition pokemon cards"
      ],
      "es": [
        "cual es la diferencia entre primera edicion y reimpresion",
        "como reconocer primera edicion en pokemon"
      ]
    },
    "answers": {
      "pt": "No Pokémon, primeira edição é a tiragem inicial; reimpressão é uma publicação posterior. Algumas coleções usam selo, outras não. As marcas variam por coleção e idioma. Confira a edição no catálogo.",
      "en": "In Pokémon, first edition is the initial printing; a reprint is a later publication. Some sets use a stamp, others do not. Marks vary by set and language. Check the catalog edition.",
      "es": "En Pokémon, primera edición es la tirada inicial; una reimpresión es una publicación posterior. Algunas colecciones usan sello, otras no. Las marcas varían según colección e idioma. Consulta la edición del catálogo."
    }
  }
] as const;
const definitions:Record<Language,RegExp>={
 pt:/^(?:o que (?:e|significa)|me explique|me explica|explique|pode explicar) /,
 en:/^(?:what is|explain|please explain) /,
 es:/^(?:que (?:es|significa)|explica|explicame|puedes explicar) /
};
export function lookupCollectorGuide(question:string,options:{hasAttachment?:boolean;cardId?:string}={}){
 if(question.length>240||options.hasAttachment||options.cardId)return null;
 const text=normalizeAtlasQuestion(question);
 for(const language of ['pt','en','es'] as const){
  const term=definitions[language].test(text)?text.replace(definitions[language],''):null;
  const entry=guides.find(g=>(g.questions[language] as readonly string[]).includes(text)||(term!==null&&(g.terms[language] as readonly string[]).includes(term)));
  if(entry)return {answer:entry.answers[language],source:'knowledge' as const,language,topicId:entry.id,
   sourceLabel:{pt:'Base revisada do Atlas · sem geração por IA',en:'Atlas reviewed knowledge · no AI generation',es:'Base revisada de Atlas · sin generación por IA'}[language],
   references:[...entry.references],reviewedAt:'2026-11-22'};
 }
 return null;
}
