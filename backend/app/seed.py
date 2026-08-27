"""
Dev-only seed script -- inserts a small amount of test data so features can
be checked against something real. Not exposed as an API endpoint on
purpose (exercise/injury "create" endpoints are deferred, see ROADMAP.md).

Run with: docker compose exec backend python -m app.seed
Safe to re-run -- it clears the three tables first.
"""

from app.core.database import SessionLocal
from app.models.exercise import Exercise
from app.models.exercise_injury import ExerciseInjury
from app.models.injury import Injury


def run():
    db = SessionLocal()
    try:
        db.query(ExerciseInjury).delete()
        db.query(Injury).delete()
        db.query(Exercise).delete()

        # Fully filled in -- exercises every content field to check rendering.
        heel_slides = Exercise(
            name="Heel Slides",
            body_part="knee",
            general_part="leg",
            video_url="https://example.com/videos/heel-slides.mp4",
            diagram_url="https://example.com/diagrams/knee.png",
            frequency="3 sets of 10, twice daily",
            equipment=["Yoga mat"],
            instructions=[
                "Lie on your back with both legs extended.",
                "Slowly slide one heel toward your glutes, bending the knee.",
                "Slide the heel back out to the starting position.",
            ],
            common_mistakes=["Letting the lower back arch off the floor."],
            modification_beginner="Use a towel under the heel to reduce friction.",
            modification_intermediate="No modification needed.",
            modification_advanced="Add ankle weights for extra resistance.",
        )
        # Left mostly empty on purpose -- checks that missing content
        # (None / empty list) renders fine, not just the fully filled case.
        ankle_alphabet = Exercise(
            name="Ankle Alphabet",
            body_part="ankle",
            general_part="leg",
            instructions=["Trace each letter of the alphabet in the air with your big toe."],
        )
        db.add_all([heel_slides, ankle_alphabet])
        db.flush()  # assigns IDs without committing yet

        ankle_sprain = Injury(name="ankle sprain")
        shin_splints = Injury(name="shin splints")
        db.add_all([ankle_sprain, shin_splints])
        db.flush()

        db.add_all([
            ExerciseInjury(exercise_id=ankle_alphabet.id, injury_id=ankle_sprain.id, effectiveness=4),
            ExerciseInjury(exercise_id=ankle_alphabet.id, injury_id=shin_splints.id, effectiveness=2),
            ExerciseInjury(exercise_id=heel_slides.id, injury_id=shin_splints.id, effectiveness=3),
        ])

        db.commit()
        print("Seeded 2 exercises, 2 injuries, 3 exercise-injury links.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
