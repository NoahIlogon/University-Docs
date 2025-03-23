# Week 4

### Association Rules
{i1, i2, ..., ik} -> j 
"If basket contains all of i1, ..., ik then it is likely to contain j"

conf(i -> j–) = support(i union j)/ support(i)

## Cloud Computing
Network based computing that takes place over the internet.  

**Virtualization:** Implement of VM's; abstraction of a physical host machine. Middle layer for security.
![[Screenshot 2025-03-15 at 2.58.51 PM.png]]
![[Screenshot 2025-03-15 at 3.05.08 PM.png]]
## **Problem:** 
![[Screenshot 2025-03-15 at 3.05.42 PM.png]]
**The Jaccard Similarity** of two sets is the size of their intersection divided by the size of their union: 
$$sim(C1, C2) = | C1 ∩ C2| / |C1 ∪ C2|$$
**The  Jaccard Distance:** 
$$d(C1, C2) = |C1 ∩ C2| / |C1 ∪ C2|$$
Intersection divided by the union
![[Screenshot 2025-03-15 at 3.29.18 PM.png]]

<<<<<<< HEAD
---
**Compressing Shingles** To compress long shingles we can hash them to say 4 bytes
- Representing a document by the set of hash values of its k shingles
- Encode as a set of vectors
![[Screenshot 2025-03-23 at 11.55.19 AM.png]]
-> Reduced a document to a single bit vector column
-> We can compute similarity/ Estimate how close they are without comparing them
-> **Hash function; if two columns are similar they will hash the same** If they are similar we will compute where they should be and they should end up the same
## Hash Function
![[Screenshot 2025-03-23 at 11.59.39 AM.png]]
-> Create a bucket eg if anything belongs in position 6 it will go into the bucket (list/dask bag) for position 6.
=======
**Distance Between 2 point stance
$$D(p1, p2) = (p1 . p2) / (|p2| * |p1|)$$
## Practice:
![[Pasted image 20250317165629.png]]
[1,2,3,4]
>>>>>>> e7a6e1b4af98ecc036608fafb7d7ac24325f8428
