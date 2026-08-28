import { getExercisesForInjury, getInjuries } from "@/lib/api";
import { getAuthCookieHeader } from "@/lib/server-auth";

export default async function InjuryPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const injuryId = Number(id);
  const cookieHeader = await getAuthCookieHeader();

  // No GET /injuries/{id} endpoint yet -- find the name from the list instead.
  const [injuries, exercises] = await Promise.all([
    getInjuries(cookieHeader),
    getExercisesForInjury(injuryId, cookieHeader),
  ]);
  const injury = injuries.find((i) => i.id === injuryId);

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <a href="/dashboard" className="text-sm text-zinc-500 hover:underline">
        &larr; All exercises
      </a>
      <h1 className="mt-2 text-2xl font-semibold capitalize text-zinc-900 dark:text-zinc-50">
        {injury?.name ?? "Unknown injury"}
      </h1>

      {exercises.length === 0 ? (
        <p className="mt-4 text-zinc-500">No exercises linked to this injury yet.</p>
      ) : (
        <ul className="mt-6 flex flex-col gap-4">
          {exercises.map((exercise) => (
            <li key={exercise.id}>
              <a
                href={`/exercises/${exercise.id}`}
                className="block rounded-lg border border-zinc-200 p-4 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-900"
              >
                <div className="flex items-center justify-between">
                  <h2 className="font-medium text-zinc-900 dark:text-zinc-50">
                    {exercise.name}
                  </h2>
                  <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    Effectiveness: {exercise.effectiveness}/5
                  </span>
                </div>
                <p className="text-sm text-zinc-500">
                  {exercise.general_part} / {exercise.body_part}
                </p>
              </a>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
