import { getExercises, getInjuries } from "@/lib/api";

export default async function Home() {
  const [exercises, injuries] = await Promise.all([getExercises(), getInjuries()]);

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
        Exercises
      </h1>

      {injuries.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
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
      )}

      {exercises.length === 0 ? (
        <p className="mt-4 text-zinc-500">No exercises yet.</p>
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
                <p className="mt-2 text-sm text-zinc-700 dark:text-zinc-300">
                  {exercise.description}
                </p>
              </a>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
