import { notFound } from "next/navigation";

import { getExercise } from "@/lib/api";

export default async function ExercisePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const exercise = await getExercise(Number(id));

  if (!exercise) {
    notFound();
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <a href="/" className="text-sm text-zinc-500 hover:underline">
        &larr; All exercises
      </a>
      <h1 className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
        {exercise.name}
      </h1>
      <p className="text-sm text-zinc-500">
        {exercise.general_part} / {exercise.body_part}
      </p>
      <p className="mt-4 text-zinc-700 dark:text-zinc-300">{exercise.description}</p>

      {/* Video, equipment, instructions, diagram -- not modeled yet, see ROADMAP.md */}

      {exercise.injuries.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-medium text-zinc-900 dark:text-zinc-50">
            Helps with
          </h2>
          <ul className="mt-3 flex flex-col gap-2">
            {exercise.injuries.map((injury) => (
              <li
                key={injury.id}
                className="flex items-center justify-between rounded-lg border border-zinc-200 px-4 py-2 dark:border-zinc-800"
              >
                <a href={`/injuries/${injury.id}`} className="capitalize hover:underline">
                  {injury.name}
                </a>
                <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                  {injury.effectiveness}/5
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </main>
  );
}
