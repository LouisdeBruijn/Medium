



*Waterfall California housing dataset*

| Table | # entries | # entries change | # unique entities | # unique entities change | Reason | Configurations flag |
| :---- | :-------- | :--------------- | :---------------- | :----------------------- | :----- | :------------------ |
| `california_housing` | 20640 | n/a | 20640 | n/a | Raw California housing data | n/a |
| `california_housing` | 16245 | -4395 | 16245 | -4395 | Select in-scope bedrooms | 1.0 |
| `california_housing` | 1451 | -14794 | 1451 | -14794 | Maximum two occupants | 2.0 |
| `california_housing` | 1358 | -93 | 1358 | -93 | House age range | [10, 80] |
| `california_housing` | 6038 | 4680 | 6038 | 4680 | Join houses w/ at least a half bedroom | True |
