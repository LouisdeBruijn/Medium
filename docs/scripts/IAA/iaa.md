#


### cohen_kappa_function
[source](https://github.com/LouisdeBruijn/Medium/blob/master/IAA/iaa.py/#L15)
```python
.cohen_kappa_function(
   ann1, ann2
)
```

---
Computes Cohen kappa for pair-wise annotators.

:param ann1: annotations provided by first annotator
:type ann1: list
:param ann2: annotations provided by second annotator
:type ann2: list

:rtype: float
:return: Cohen kappa statistic

----


### fleiss_kappa_function
[source](https://github.com/LouisdeBruijn/Medium/blob/master/IAA/iaa.py/#L43)
```python
.fleiss_kappa_function(
   M
)
```

---
Computes Fleiss' kappa for group of annotators.

:param M: a matrix of shape (:attr:'N', :attr:'k') with 'N' = number of subjects and 'k' = the number of categories.
'M[i, j]' represent the number of raters who assigned the 'i'th subject to the 'j'th category.
---
:type: numpy matrix

:rtype: float
:return: Fleiss' kappa score
