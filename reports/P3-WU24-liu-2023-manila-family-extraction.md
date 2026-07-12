# P3-WU24 Liu et al. 2023 Manila family extraction

Date: 2026-07-12

Status: 19 PMEL-based source families and location-specific arrival ranges are
extracted; zero records are promoted to PEGS simulation scenarios.

The primary HTML article became available through its HTTP endpoint. Tables 4--6
define a 22-subfault PMEL SIFT Manila source database and three scenario
families:

- Mw 7.5: 11 locations, 96 by 23 km rupture, 3.1 m mean slip;
- Mw 8.1: 5 locations, 192 by 46 km rupture, 6.3 m mean slip; and
- Mw 8.5: 3 locations, 303 by 74 km rupture, 10.0 m mean slip.

The source tables report 90-degree rake and location-specific longitude,
latitude, strike, dip and depth. The article also reports separate modelled
arrival ranges for Nanao, Shanwei, Macao, Boao and Sanya. For example, the
Mw 8.1 family spans 2.6--3.8 h at Nanao, 3.0--3.8 h at Shanwei, 4.0--4.5 h at
Macao, 2.3--2.6 h at Boao and 2.4--2.7 h at Sanya. These values are retained by
magnitude family and location; none becomes a universal South China arrival.

The extraction does not satisfy `ManilaScenario`: rise time and rupture
velocity are absent, and the arrival threshold definition is not explicit in
the extracted text. The repository therefore retains `scenarios: []`. The
families can support later source selection and warning-site design after
dynamic rupture parameters are independently sourced.

Primary source: Liu et al. (2023), *Oceanologia et Limnologia Sinica* 54(2),
331--350, `http://qdhys.cnjournals.com/html/hyyhz/2023/2/20230202.htm`.
