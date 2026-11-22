// Limited spelling repair for reviewed FAQ vocabulary, never card names/codes,
// prices, negations or arbitrary sentences. A corrected question still has to
// match a whole supported intent before it can receive a local answer.
const vocabulary=['sleeve','toploader','grading','holografica','holografico',
 'reverse','pokemon','diferenca','difference','diferencia','significa',
 'conservacao','colecao','collection','coleccion','raridade','rarity',
 'rareza','graduacao','reimpressao','energia','energy','comecar','iniciar','colecionar'];
const validWords=['diferenciar','significam','significan'];
const regional={pt:['diferenca','conservacao','colecao','raridade','graduacao','reimpressao'],
 en:['difference','collection','rarity','energy'],es:['diferencia','coleccion','rareza']};
function oneEdit(a:string,b:string){
 if(Math.abs(a.length-b.length)>1)return false;
 let i=0;while(i<a.length&&i<b.length&&a[i]===b[i])i++;
 if(i===a.length||i===b.length)return true;
 if(a.length===b.length)return a.slice(i+1)===b.slice(i+1)||
  (a[i]===b[i+1]&&a[i+1]===b[i]&&a.slice(i+2)===b.slice(i+2));
 return a.length>b.length?a.slice(i+1)===b.slice(i):a.slice(i)===b.slice(i+1);
}
export function repairAtlasSpelling(text:string){
 let corrections=0;
 const language=/\b(what|how|which|the|between)\b/.test(text)?'en':
  /^(?:cual |que |como (?:guardar mis|proteger mis|identificar la))|\b(una|las|los)\b/.test(text)?'es':
  /^(?:o que |oq |o q |oque |q |qual |como )/.test(text)?'pt':null;
 const terms=vocabulary.filter(term=>!language||!Object.entries(regional).some(([lang,words])=>lang!==language&&words.includes(term)));
 const repaired=text.replace(/\b[a-z]{5,}\b/g,word=>{
  if(terms.includes(word)||validWords.includes(word))return word;
  const candidates=terms.filter(term=>oneEdit(word,term));
  if(candidates.length!==1)return word;
  corrections++;return candidates[0];
 });
 return corrections<=2?repaired:text;
}
export function expandAtlasShorthand(text:string){
 let result=text.replace(/^(oq|o q|oque|q|o que) eh /,'$1 e ')
  .replace(/^(?:oq|o q|oque) (e|significa) /,'o que $1 ')
  .replace(/^q (e|significa) /,'o que $1 ')
  .replace(/^qual e a diferenca entre /,'qual a diferenca entre ')
  .replace(/^qual (?:e )?diferenca entre /,'qual a diferenca entre ')
  .replace(/\btop[ -]loaders?\b/g,'toploader');
 // No substring extraction: extra requests must remain visible to the matcher.
 if(/^(?:carta|card) (?:nm|near mint|lp|mp|dmg)$/.test(result)){
  result=result.startsWith('card ')?'what is '+result:'o que significa '+result;
 }
 if(/^(?:sleeve (?:e|ou|vs) toploader|sleeve|toploader)$/.test(result)){
  result=result==='sleeve'||result==='toploader'?'o que e um '+result:'qual a diferenca entre sleeve e toploader';
 }
 if(/^holo (?:e|ou|vs) reverse holo$/.test(result))result='qual a diferenca entre holo e reverse holo';
 return result;
}
