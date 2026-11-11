import { allTopics, allPapers } from '../../lib/data';
import spec from '../../data/spec.json';
const tools = [{"t": "Practice player", "u": "/practice/", "kind": "Tool"}, {"t": "Mini-mock builder", "u": "/mock/", "kind": "Tool"}, {"t": "Question of the day", "u": "/today/", "kind": "Tool"}, {"t": "Spec checklist", "u": "/specification/", "kind": "Tool"}, {"t": "Grade boundaries and calculator", "u": "/grade-boundaries/", "kind": "Tool"}, {"t": "Exam dates", "u": "/exam-dates/", "kind": "Tool"}, {"t": "Revision planner", "u": "/planner/", "kind": "Tool"}, {"t": "What comes up (analysis)", "u": "/analysis/", "kind": "Tool"}, {"t": "What came up last summer", "u": "/what-came-up/", "kind": "Tool"}, {"t": "Every paper as a timeline", "u": "/timeline/", "kind": "Tool"}, {"t": "Tutors", "u": "/tutors/", "kind": "Tool"}, {"t": "Flashcards", "u": "/flashcards/", "kind": "Tool"}, {"t": "Essays and timed essay", "u": "/essays/", "kind": "Tool"}, {"t": "Define it drill", "u": "/practice/define/", "kind": "Tool"}, {"t": "Methods in Context questions", "u": "/questions/type/methods-in-context/", "kind": "Tool"}, {"t": "Outline and explain (10-mark) questions", "u": "/questions/type/outline-and-explain/", "kind": "Tool"}, {"t": "Applying material from the Item: analyse questions", "u": "/questions/type/analyse/", "kind": "Tool"}, {"t": "Essay questions", "u": "/questions/type/essays/", "kind": "Tool"}, {"t": "Key terms flashcards", "u": "/flashcards/", "kind": "Tool"}];
export function GET() {
  const items = [
    ...allTopics.map((t) => ({ t: t.name, k: t.group, u: `/questions/${t.slug}/`, kind: 'Topic' })),
    ...allPapers.map((p) => ({ t: `${p.series} ${p.qual === 'AS' ? 'AS ' : ''}${p.paper}`, k: p.spec, u: `/past-papers/${p.slug}/`, kind: 'Paper' })),
  ...spec.flatMap((s) => s.statements.map((st) => ({ t: `${st.id} ${st.text.slice(0, 80)}`, k: s.title, u: `/questions/${s.topic}/`, kind: 'Spec statement' }))),
    ...tools,
  ];
  return new Response(JSON.stringify(items), { headers: { 'Content-Type': 'application/json' } });
}
