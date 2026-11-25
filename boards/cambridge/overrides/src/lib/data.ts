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

const SERIES_ORDER: Record<string, number> = { March: 1, June: 2, November: 3 };
/** Newest first: year, then November > June > March, then paper and question. */
export const seriesRank = (s: string) => (s === 'Specimen' ? 0 : Number(s.split(' ')[1]) * 10 + (SERIES_ORDER[s.split(' ')[0]] || 0));

export function questionsForTopic(slug: string): Q[] {
  return allQuestions.filter((q) => q.topics.includes(slug)).sort((a, b) => seriesRank(b.series) - seriesRank(a.series) || a.paper.localeCompare(b.paper) || String(a.comp).localeCompare(String(b.comp)) || a.question.localeCompare(b.question, undefined, { numeric: true }));
}

export const AQA_MATERIALS = 'https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-international-as-and-a-level-sociology-9699/';
export const Cambridge_MATERIALS = AQA_MATERIALS;

/** Where a topic sits: badge number (colour), short label, motif and where it is examined. */
export const GROUPS: [string, string, number, string, string][] = [
  ['Paper 1: Socialisation and identity', 'P1', 1, 'people', 'Paper 1 Section A (and Q4/Q5 in Section B); AS Level'],
  ['Paper 1: Methods of research', 'P1', 1, 'stats', 'Paper 1: Q1, Q2 and the Section B essay choice; AS Level'],
  ['Paper 2: The family', 'P2', 2, 'people', 'Paper 2, all questions; AS Level'],
  ['Paper 3: Education', 'P3', 3, 'book', 'Paper 3, all questions; A Level'],
  ['Paper 4: Globalisation', 'P4', 4, 'globe', 'Paper 4 Section A (choose two essays from the paper); A Level'],
  ['Paper 4: Media', 'P4', 4, 'globe', 'Paper 4 Section B (choose two essays from the paper); A Level'],
  ['Paper 4: Religion', 'P4', 4, 'book', 'Paper 4 Section C (choose two essays from the paper); A Level'],
];
export function groupInfo(group: string) {
  const g = GROUPS.find((x) => x[0] === group) || GROUPS[0];
  return { group: g[0], short: g[1], badge: g[2], motif: g[3], where: g[4], area: g[0].replace(/^Paper \d: /, '') };
}

/** The question sentence of a part: Cambridge questions are one or two sentences, so the extracted text is the title. */
export function essayTitle(text: string): string {
  return (text || '').replace(/\[\d+\]/g, '').replace(/\s+/g, ' ').trim();
}
