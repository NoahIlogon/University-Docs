## Min Hashing
The similarity of two signatures is the fraction of the hash functions in which they agree.
![[Screenshot 2025-03-23 at 12.10.49 PM.png]]
## LSH: First cut:
Use a func f(x,y) that tells whether x and y is a candidate pairL a pair of elements whose similarity must be evaluated
- Each pair of documents that hash into the same bucked is a candidate pair
- Arrange that similar columns are likely to hash to the same bucket with high probability
- **Candidate Pairs** are those that hash to the same bucket.![[Screenshot 2025-03-23 at 12.26.36 PM.png]]
 ![[Screenshot 2025-03-23 at 12.27.29 PM.png]]
 ---

 **We can then look at our dataset as an interconnected graph**
 - Social Networks
 - Trends
 - Information Networks
 
 **E.G Web as a graph**
 Nodes: Webpages
 Edges: Hyperlinks

Ranking Nodes on the graph on basis of importance![[Screenshot 2025-03-23 at 1.00.34 PM.png]]
**-> Parallel BFS!**
### **Pagerank**: The  “Flow“ Formulation

-> Links as votes
	- Page is more important if it has more links
	- Links from important pages count more
Figure out which nodes are important

![[Screenshot 2025-03-23 at 1.23.43 PM.png]]
## Simple Recursive Formulation
![[Screenshot 2025-03-23 at 1.26.53 PM.png]]
- A page is important if it is pointed to by other important pages
---
![[Screenshot 2025-03-23 at 1.40.22 PM.png]]

| Node |   1 |  2  | 3   | 4   |
| :--- | --: | :-: | --- | --- |
| 1    |   0 |  1  | 0   | 0   |
| 2    | 1/2 |  0  | 0   | 0   |
| 3    | 1/2 |  0  | 0   | 1   |
| 4    |   0 |  0  | 1   | 0   |
Assume all columns sum to 1
- All columns represent outgoing links
- for node 1. links to 2 & 3 are 1/2 because 50% of the time you'll end up at node 2 and 50% of the time you'll end up at node 3 and 0 chances you'll end up at 1 or 4
![[IMG_5312.jpeg]]
---
 ![[Screenshot 2025-03-23 at 2.31.39 PM.png]]