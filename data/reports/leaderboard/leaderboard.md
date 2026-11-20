### all (75 tasks x 4 attempts)

| Model | pass@1 | 95% CI (tasks) | pass@4 | pass^4 | tests passed | truncated | infra err | out tokens | $/task |
|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash-1017 | 0.940 | 0.90-0.97 | 0.987 | 0.853 | 0.978 | 2.0% | 0.0% | 4239 | 0.0119 |
| openai/gpt-oss-120b | 0.523 | 0.43-0.61 | 0.720 | 0.293 | 0.937 | 0.0% | 0.0% | 1170 | 0.0041 |
| openai/gpt-oss-20b | 0.380 | 0.30-0.46 | 0.680 | 0.107 | 0.855 | 0.0% | 0.0% | 987 | 0.0015 |

### test (37 tasks x 4 attempts)

| Model | pass@1 | 95% CI (tasks) | pass@4 | pass^4 | tests passed | truncated | infra err | out tokens | $/task |
|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash-1017 | 0.946 | 0.88-0.99 | 0.973 | 0.892 | 0.991 | 0.7% | 0.0% | 3847 | 0.0108 |
| openai/gpt-oss-120b | 0.541 | 0.41-0.67 | 0.730 | 0.297 | 0.955 | 0.0% | 0.0% | 1092 | 0.0039 |
| openai/gpt-oss-20b | 0.392 | 0.28-0.51 | 0.676 | 0.108 | 0.867 | 0.0% | 0.0% | 946 | 0.0015 |

