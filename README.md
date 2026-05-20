# V-Fit

# Directory Organization 
```bash 
ai-fitness-app/
│
├── README.md
├── shared/
│   ├── pose_estimation.py
│   ├── keypoint_utils.py
│   ├── angle_calculator.py
│   ├── drawing_utils.py
│   └── constants.py
│
├── form_check/
│   ├── form_checker.py
│   ├── exercise_classifier.py
│   ├── rules/
│   │   ├── squat_rules.py
│   │   ├── pushup_rules.py
│   │   ├── plank_rules.py
│   │   └── deadlift_rules.py
│   ├── feedback_generator.py
│   └── tests/
│       ├── test_squat.py
│       ├── test_pushup.py
│       └── test_plank.py
│
├── body_analysis/
│   ├── body_analyzer.py
│   ├── posture_analyzer.py
│   ├── imbalance_detector.py
│   ├── body_fat_estimator.py
│   └── tests/
│       └── test_body_analysis.py
│
└── recommendation/
    ├── workout_recommender.py
    ├── nutrition_recommender.py
    ├── progress_tracker.py
    ├── ai_assistant.py
    └── rules/
        ├── workout_rules.py
        ├── nutrition_rules.py
        └── progression_rules.py
├── data/
├── raw/
│   ├── videos/
│   ├── images/
│   └── body_scans/
│
├── processed/
│   ├── keypoints/
│   ├── form_check_results/
│   └── body_analysis_results/
│
├── exercise_database/
│   ├── exercises.json
│   ├── common_errors.json
│   └── muscle_groups.json
│
└── nutrition_database/
    ├── foods.json
    ├── meals.json
    └── macros.json
├── frontend/
├── package.json
├── public/
└── src/
    ├── App.jsx
    ├── main.jsx
    │
    ├── pages/
    │   ├── Home.jsx
    │   ├── FormCheck.jsx
    │   ├── BodyAnalysis.jsx
    │   ├── WorkoutPlan.jsx
    │   └── NutritionPlan.jsx
    │
    ├── components/
    │   ├── CameraView.jsx
    │   ├── PoseOverlay.jsx
    │   ├── FeedbackBox.jsx
    │   ├── WorkoutCard.jsx
    │   └── MealPlanCard.jsx
    │
    ├── api/
    │   ├── formCheckApi.js
    │   ├── bodyAnalysisApi.js
    │   └── recommendationApi.js
    │
    └── utils/
        └── camera.js
├── tests/
│   ├── test_camera.py
│   ├── test_form_check.py
│   ├── test_body_analysis.py
│   └── test_recommendation.py
│
├── scripts/
│   ├── collect_video_data.py
│   └── extract_keypoints.py
│
└── notebooks/
    ├── pose_estimation_demo.ipynb
    ├── form_check_experiments.ipynb
    └── body_analysis_experiments.ipynb
```
