import questions from '../data/questions.json';
import papers from '../data/papers.json';
import topics from '../data/topics.json';

export type Q = (typeof questions)[number];
export type Paper = (typeof papers)[number];
export type Topic = (typeof topics)[number];

export const allQuestions: Q[] = questions as Q[];
export const allPapers: Paper[] = papers as Paper[];
export const allTopics: Topic[] = topics as Topic[];

export const byId = new Map(allQuestions.map((q) => [q.id, q]));
export const topicByslug = new Map(allTopics.map((t) => [t.slug, t]));

export function questionsForTopic(slug: string): Q[] {
  return allQuestions.filter((q) => q.topics.includes(slug)).sort((a, b) => b.year - a.year || a.paper.localeCompare(b.paper) || a.question.localeCompare(b.question, undefined, { numeric: true }));
}

export const AQA_MATERIALS = 'https://www.aqa.org.uk/subjects/sociology/a-level/sociology-7192/assessment-resources';

/** Where a topic sits: badge number (colour), short label, motif and where it is examined. */
export const GROUPS: [string, string, number, string, string][] = [
  // group, short, badge colour, motif, where examined
  ['Paper 1: Education', 'P1', 1, 'book', 'A-level Paper 1 Section A; AS Paper 1'],
  ['Theory and Methods', 'T&M', 3, 'stats', 'A-level Paper 1 (Methods in Context and Theory and Methods) and Paper 3 Section B; AS Papers 1 and 2'],
  ['Paper 2: Culture and Identity', 'P2', 2, 'people', 'A-level Paper 2 Section A (option); AS Paper 2 Section B (option)'],
  ['Paper 2: Families and Households', 'P2', 2, 'people', 'A-level Paper 2 Section A (option); AS Paper 2 Section B (option)'],
  ['Paper 2: Health', 'P2', 2, 'neuron', 'A-level Paper 2 Section A (option); AS Paper 2 Section B (option)'],
  ['Paper 2: Work, Poverty and Welfare', 'P2', 2, 'coins', 'A-level Paper 2 Section A (option); AS Paper 2 Section B (option)'],
  ['Paper 2: Beliefs in Society', 'P2', 2, 'book', 'A-level Paper 2 Section B (option)'],
  ['Paper 2: Global Development', 'P2', 2, 'globe', 'A-level Paper 2 Section B (option)'],
  ['Paper 2: The Media', 'P2', 2, 'globe', 'A-level Paper 2 Section B (option)'],
  ['Paper 2: Stratification and Differentiation', 'P2', 2, 'scales', 'A-level Paper 2 Section B (option)'],
  ['Paper 3: Crime and Deviance', 'P3', 4, 'scales', 'A-level Paper 3 Section A'],
];
export function groupInfo(group: string) {
  const g = GROUPS.find((x) => x[0] === group) || GROUPS[0];
  return { group: g[0], short: g[1], badge: g[2], motif: g[3], where: g[4], area: g[0].replace(/^Paper \d: /, '') };
}

/** The question sentence of a part: the text after the Item (or after the label), without '[n marks]' and 'Extra space'. */
export function essayTitle(text: string): string {
  let t = (text || '').replace(/Extra space/g, '').replace(/\[\d+ marks?\]/g, '');
  const k = Math.max(t.lastIndexOf('Applying material'), t.search(/\n(Evaluate|Outline|Using one|Define|Examine|Assess|Discuss)/));
  if (k > 0) t = t.slice(k);
  t = t.replace(/^(Topic [AB]\d[^\n]*|Section [AB][^\n]*|Education|Answer all questions\.?|Crime and Deviance|Methods in Context|Theory and Methods)\s*\n/gm, '').replace(/^\d \d\s*/m, '');
  return t.replace(/\s+/g, ' ').trim();
}
