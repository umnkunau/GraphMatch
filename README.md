# GraphMatch: Knowledge Graphs for Allogeneic Stem Cell Matching
 ![pda](https://github.com/user-attachments/assets/cf342d9e-0a50-4e81-a961-02c5973640be)

GraphMatch (GM) is a scalable graph database solution based on Neo4j for storing and searching variable resolution genotype information supporting Patient/Donor matching for stem cell transplants. Performance timing remained linear with the number of edges, even at a production scale.  

We developed GraphMatch (GM), a scalable graph database solution for storing and searching variable-resolution HLA genotype markers. As a test set, we expanded the World Marrow Donor Association (WMDA) validation set based on the IPD-IMGT/HLA Database version 2.16 to create a synthetic production data set of 1 million patients and 10 million donors.

Single-patient identity search times range from 218.5 milliseconds per patient for 2 million donors to 1201.4 milliseconds per patient for 10 million donors. Search performance timing remained linear with the number of edges, even at a production scale.

In general, GM demonstrates the usefulness of graph databases as a flexible platform for scalable matching solutions.
