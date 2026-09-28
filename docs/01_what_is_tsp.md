# 01 — What Is TSP? (From Absolute Zero)

## The pizza shop story

You own a pizza shop. Today there are **5 orders** at 5 different houses.

Rules:
1. Start at your shop.
2. Visit each house **exactly once**.
3. Come back to the shop.
4. Travel the **shortest total distance** (less petrol = more profit).

The question — *"in what order should I visit?"* — is the
**Travelling Salesman Problem (TSP)**. It is one of the most famous
problems in computer science, studied since the 1930s.

## Why not just try everything?

For 5 houses (shop fixed as start), the remaining 4 houses can be ordered
in 4 × 3 × 2 × 1 = **24 ways**. A computer checks 24 paths in a blink.
Easy.

But watch what happens when houses grow (shop fixed, so (N−1)! orders):

| Houses | Possible orders | Time to check all |
|---|---|---|
| 5 | 24 | blink of an eye |
| 10 | 362,880 | seconds |
| 12 | 39 million | minutes–hours |
| 15 | 87 billion | days |
| 20 | 121 million billion | longer than your life |
| 50 | (a number with 62 digits) | longer than the universe |

This explosion is called **factorial growth**, and it is the entire reason
this project exists: we cannot "just try everything" for real maps, so we
need **smart methods** that find *almost*-shortest paths quickly.

## Key words you will see everywhere

- **City** = a house (a point with x, y position on the map).
- **Route / tour** = one full visiting order, e.g. Shop → House3 → House5 → … → Shop.
- **Depot** = the shop (City 1). Fixed as start and end, always.
- **Optimal route** = the shortest possible route (only knowable by checking
  everything, i.e. only for small maps).
- **Gap %** = how much longer our answer is than the best known, in percent.
  0% = perfect. 100% = twice as long. Lower is better.
- **Heuristic** = a smart shortcut method. Fast, usually good, but with no
  100% guarantee (unlike checking everything).

## What "solving" means in this project

Given a set of city positions, output:
1. A visiting order (list like `[1, 4, 3, 2, 5]`, meaning City1 → City4 → …).
2. Its total length (e.g. `227.35`).

Every method in this project takes the same input and gives the same kind
of output — that is what lets us race them fairly (file 02 explains the
racers, files 04–05 explain the races).
