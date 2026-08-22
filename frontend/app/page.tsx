import { getExercises } from "@/lib/api";

export default async function Home() {
  const exercises = await getExercises();

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
        Exercises
      </h1>

      {exercises.length === 0 ? (
        <p className="mt-4 text-zinc-500">No exercises yet.</p>
      ) : (
        <ul className="mt-6 flex flex-col gap-4">
          {exercises.map((exercise) => (
            <li
              key={exercise.id}
              className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800"
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
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
