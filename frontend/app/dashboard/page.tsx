import { getExercises, getGeneralParts, getInjuries, getPrograms } from "@/lib/api";
import { getAuthCookieHeader } from "@/lib/server-auth";

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q } = await searchParams;
  const cookieHeader = await getAuthCookieHeader();
  const [exercises, injuries, generalParts, programs] = await Promise.all([
    getExercises(q, cookieHeader),
    getInjuries(cookieHeader),
    getGeneralParts(cookieHeader),
    getPrograms(cookieHeader),
  ]);

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
        Exercises
      </h1>

      <div className="mt-4">
        <p className="text-xs font-medium uppercase tracking-wide text-zinc-400">
          Your Programs
        </p>
        <div className="mt-2 flex flex-wrap gap-2">
          {programs.map((program) => (
            <a
              key={program.id}
              href={`/programs/${program.id}`}
              className="rounded-full border border-zinc-200 px-3 py-1 text-sm text-zinc-700 hover:bg-zinc-100 dark:border-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-900"
            >
              {program.name}
            </a>
          ))}
          <a
            href="/programs/new"
            className="rounded-full border border-dashed border-zinc-300 px-3 py-1 text-sm text-zinc-500 hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-900"
          >
            + New Program
          </a>
        </div>
      </div>

      {/* Plain GET form -- submitting navigates to /dashboard?q=..., which the
          Server Component above reads via searchParams. No client-side
          JS/state needed, unlike a typical React controlled-input search. */}
      <form method="GET" className="mt-4">
        <input
          type="search"
          name="q"
          defaultValue={q ?? ""}
          placeholder="Search for an exercise..."
          className="w-full rounded-full border border-zinc-200 px-4 py-2 text-sm text-zinc-900 placeholder:text-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50"
        />
      </form>

      {generalParts.length > 0 && (
        <div className="mt-4">
          <p className="text-xs font-medium uppercase tracking-wide text-zinc-400">
            Collections
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            {generalParts.map((part) => (
              <a
                key={part}
                href={`/collections/${encodeURIComponent(part)}`}
                className="rounded-full border border-zinc-200 px-3 py-1 text-sm capitalize text-zinc-700 hover:bg-zinc-100 dark:border-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-900"
              >
                {part}
              </a>
            ))}
          </div>
        </div>
      )}

      {injuries.length > 0 && (
        <div className="mt-4">
          <p className="text-xs font-medium uppercase tracking-wide text-zinc-400">
            By injury
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            {injuries.map((injury) => (
              <a
                key={injury.id}
                href={`/injuries/${injury.id}`}
                className="rounded-full border border-zinc-200 px-3 py-1 text-sm capitalize text-zinc-700 hover:bg-zinc-100 dark:border-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-900"
              >
                {injury.name}
              </a>
            ))}
          </div>
        </div>
      )}

      {exercises.length === 0 ? (
        <p className="mt-4 text-zinc-500">
          {q ? `No exercises match "${q}".` : "No exercises yet."}
        </p>
      ) : (
        <ul className="mt-6 flex flex-col gap-4">
          {exercises.map((exercise) => (
            <li key={exercise.id}>
              <a
                href={`/exercises/${exercise.id}`}
                className="block rounded-lg border border-zinc-200 p-4 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-900"
              >
                <h2 className="font-medium text-zinc-900 dark:text-zinc-50">
                  {exercise.name}
                </h2>
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
