BEGIN;

-- on the first run of the janitor, I removed racer_ids from race results that contained the same racer in the same race
-- but the racers persisted with 0 owned results. they should have been removed, because having a 0 race racers is not
-- baked into existing logic and doesn't make for a very interesting piece of data

WITH hanging_racer_ids AS (
    SELECT
      DISTINCT r.id AS racer_id
    FROM racer r
    LEFT JOIN race_result rr
      ON r.id = rr.racer_id
    WHERE
      rr.racer_id IS NULL
)
DELETE FROM racer r
WHERE
  r.id IN (SELECT racer_id from hanging_racer_ids)
RETURNING *;

COMMIT;

-- holding onto the result set because it's fun to see how most are common names
select ' id   | first_name  | middle_name |  last_name  | gender | age_lower | age_upper | location
-------+-------------+-------------+-------------+--------+-----------+-----------+----------
 11763 | David       |             | Johnson     | male   |           |           |
 23811 | Michael     |             | Wagner      | male   |           |           |
 17942 | John        |             | Olson       | male   |           |           |
 25157 | Patrick     |             | Gallagher   | male   |           |           |
 11894 | David       |             | Peters      | male   |           |           |
  5925 | Aaron       |             | Nelson      | male   |           |           |
 50971 | Tom         |             | Wood        | male   |           |           |
 21458 | Louis       |             | Muench      | male   |           |           |
 11705 | David       |             | Gorman      | male   |           |           |
 10302 | Christopher |             | Johnson     | male   |           |           |
 31089 | William     |             | Clark       | male   |           |           |
 11565 | David       |             | Anderson    | male   |           |           |
 11595 | David       |             | Benson      | male   |           |           |
 23995 | Mike        | T           | Johnson     | male   |           |           |
 19996 | Kevin       |             | Krueger     | male   |           |           |
 50398 | Ted         |             | Gephart     | male   |           |           |
 31177 | William     |             | Martin      | male   |           |           |
  9837 | Charles     |             | Smith       | male   |           |           |
 18037 | John        |             | Southworth  | male   |           |           |
 47353 | Mitch       |             | Miller      | male   |           |           |
 18084 | John        |             | Walker      | male   |           |           |
 25301 | Paul        |             | Carlson     | male   |           |           |
 16701 | Jeffrey     |             | Olson       | male   |           |           |
 22259 | Mark        |             | Miller      | male   |           |           |
 27699 | Sarah       | L           | Anderson    | female |           |           |
 27484 | Sam         |             | Williams    | male   |           |           |
 30079 | Timothy     |             | Peterson    | male   |           |           |
 25708 | Peter       |             | Huot        | male   |           |           |
 22524 | Mary        |             | Anderson    | female |           |           |
 11267 | Daniel      |             | Johnson     | male   |           |           |
 11902 | David       |             | Pramann     | male   |           |           |
 11866 | David       |             | Nelson      | male   |           |           |
 23013 | Matthew     |             | Ryan        | male   |           |           |
 31156 | William     | E           | Johnson     | female |           |           |
 15698 | James       |             | Allen       | male   |           |           |
  8088 | Benjamin    |             | Koenig      | male   |           |           |
 18216 | Jon         |             | Webster     | male   |           |           |
 26741 | Robert      | G           | Hansen      | male   |           |           |
 11584 | David       |             | Bartol      | male   |           |           |
  7032 | Andrew      |             | Meyer       | male   |           |           |
 31077 | William     |             | Brown       | male   |           |           |
 29098 | Susan       |             | Davis       | female |           |           |
 23764 | Michael     |             | Smith       | male   |           |           |
 23725 | Michael     |             | Risse       | male   |           |           |
 23032 | Matthew     |             | Smith       | male   |           |           |
 23480 | Michael     | B           | Finn        | male   |           |           |
 15518 | Jack        |             | Zabrowski   | male   |           |           |
 17886 | John        | H           | Lyons       | male   |           |           |
 14171 | Gary        |             | Meader      | male   |           |           |
 11804 | David       |             | Lindgren    | male   |           |           |
 43089 | Jill        |             | Heath       | female |           |           |
 23657 | Michael     | A           | Miller      | male   |           |           |
 30449 | Tony        | E           | Schubert    | male   |           |           |
 23997 | Mike        |             | Joyce       | male   |        65 |        69 |
 37367 | Angie       | M           | Johnson     | female |           |           |
 25434 | Paul        |             | Olson       | male   |           |           |
 11891 | David       |             | Pedersen    | male   |           |           |
 14671 | Gregory     |             | Miller      | male   |           |           |
 12013 | David       |             | Wilcox      | male   |           |           |
 11315 | Daniel      |             | Nelson      | male   |           |           |
 18147 | Jon         | R           | Freedlund   | male   |           |           |
 17741 | John        |             | Floberg     | male   |           |           |
 13461 | Eric        |             | Olson       | male   |           |           |
 44235 | Karen       |             | Olson       | female |        41 |        41 |
 29722 | Thomas      |             | Meyer       | male   |           |           |
 23603 | Michael     |             | Lee         | male   |           |           |
 29338 | Taylor      |             | Healy       | female |           |           |
 15844 | James       |             | Kelley      | male   |           |           |
 13364 | Eric        |             | Brandt      | male   |           |           |
 10329 | Christopher |             | Martin      | male   |           |           |
 17647 | John        | P           | Bauer       | male   |           |           |
 23581 | Michael     |             | Kirk        | male   |           |           |
 29535 | Thomas      |             | Anderson    | male   |           |           |
 39424 | Cliff       |             | Reithel     | male   |           |           |
  9729 | Chad        |             | Olson       | male   |           |           |
 11996 | David       | S           | Wagner      | male   |           |           |
 19136 | Karl        |             | Schroeder   | male   |           |           |
 30848 | Vince       |             | Beacom      | male   |           |           |
 18051 | John        |             | Strand      | male   |           |           |
 19751 | Ken         |             | Kuznia      | male   |           |           |
 14155 | Gary        |             | Johnson     | male   |           |           |
 22203 | Mark        |             | Johnson     | male   |           |           |
 12021 | David       |             | Wood        | male   |           |           |
 13648 | Erik        |             | Olson       | male   |           |           |
 45771 | Lori        |             | Ekman       | female |        55 |        55 |
 26667 | Robert      |             | Carr        | male   |           |           |
  6993 | Andrew      |             | Johnson     | male   |           |           |
 14618 | Gregory     |             | Anderson    | male   |           |           |
 25216 | Patrick     |             | O''Connell   | male   |           |           |
 27897 | Scott       |             | Cooper      | male   |           |           |
 11740 | David       |             | Hill        | male   |           |           |
 30226 | Todd        |             | Williams    | male   |           |           |
 16671 | Jeffrey     |             | Johnson     | male   |           |           |
 27021 | Roger       |             | Prevot      | male   |           |           |
 30906 | Wade        |             | Johnson     | male   |           |           |
  8321 | Bill        |             | Konieczki   | female |           |           |
 40481 | Donald      | W           | Olson       | male   |        66 |        66 |
 31064 | William     |             | Bauer       | male   |           |           |
 17839 | John        |             | Keane       | male   |           |           |
 13422 | Eric        |             | Johnson     | male   |           |           |
 31220 | William     |             | Reeves      | male   |           |           |
 40758 | Elizabeth   |             | Barr        | female |           |           |
 25742 | Peter       |             | Mack        | male   |           |           |
 25179 | Patrick     |             | Johnson     | male   |           |           |
 28850 | Steve       |             | Smith       | male   |           |           |
 25116 | Patricia    | A           | Olson       | female |           |           |
 20012 | Kevin       |             | Mahoney     | male   |           |           |
 22736 | Matt        |             | Anderson    | male   |           |           |
 26643 | Robert      |             | Baker       | male   |           |           |
 17820 | John        | J           | Hutchinson  | male   |           |           |
  7985 | Ben         |             | Larson      | male   |           |           |
 27921 | Scott       |             | Gislason    | male   |           |           |
  8795 | Brian       |             | Anderson    | male   |           |           |
 12456 | Don         |             | Olson       | male   |           |           |
 20616 | Larry       |             | Behne       | male   |           |           |
 43643 | John        |             | Thiel       | male   |           |           |
 22349 | Mark        |             | Stange      | male   |           |           |
 17116 | Jessica     |             | Johnson     | female |           |           |
 26279 | Reid        |             | Gilbertson  | male   |           |           |
 23371 | Michael     |             | Alexson     | male   |           |           |
 16803 | Jennifer    |             | Anderson    | female |           |           |
 18061 | John        |             | Thompson    | male   |           |           |
 35605 | Daniel      |             | Milavitz    | male   |        17 |        17 |
  8001 | Ben         | E           | Nelson      | male   |           |           |
 37493 | Anna        |             | Slate       | male   |           |           |
 30320 | Tom         |             | Meyer       | male   |           |           |
 23369 | Michael     |             | Adams       | male   |           |           |
 29802 | Thomas      |             | Tessendorf  | male   |           |           |
 38189 | Bo          |             | Karlsson    | male   |        55 |        59 |
 27994 | Scott       |             | Olson       | male   |           |           |
 23561 | Michael     |             | Johnson     | male   |           |           |
 11303 | Daniel      |             | Meyer       | male   |           |           |
 14142 | Gary        |             | Gerst       | male   |           |           |
 13962 | Frank       |             | Gangi       | male   |           |           |
 17739 | John        |             | Fitzgerald  | male   |           |           |
 14035 | Frederick   | J           | Kundert     | male   |           |           |
 23687 | Michael     |             | O''Brien     | male   |           |           |
 25617 | Peter       |             | Aggen       | male   |           |           |
 47380 | Molly       |             | Hagstrom    | female |           |           |
 20536 | Kyle        |             | Fredrickson | male   |           |           |
 11172 | Dane        | R           | Johnson     | male   |           |           |
 43475 | John        |             | Barkei      | male   |           |           |
 29540 | Thomas      |             | Barry       | male   |           |           |
 26648 | Robert      |             | Berg        | male   |           |           |
 18102 | John        |             | Wood        | male   |           |           |
 23049 | Matthew     |             | Thomas      | male   |           |           |
 15834 | James       |             | Johnson     | male   |           |           |
  6973 | Andrew      |             | Harris      | male   |           |           |
 11895 | David       |             | Peterson    | male   |           |           |
 17706 | John        |             | DeFord      | male   |           |           |
 38444 | Brian       |             | Carlson     | male   |           |           |
 22284 | Mark        |             | Olson       | male   |           |           |
 17445 | Joe         |             | Duffy       | male   |           |           |
  5919 | Aaron       |             | Johnson     | male   |           |           |
 26882 | Robert      |             | Smith       | male   |           |           |
 24632 | Nicholas    |             | Schneider   | male   |           |           |
  6925 | Andrew      |             | Dahl        | male   |           |           |
 17631 | John        |             | Anderson    | male   |           |           |
 49241 | Sam         | H           | Johnson     | male   |         1 |        11 |
 45731 | Lloyd       | B           | Anderson    | male   |           |           |
 10335 | Christopher |             | Miller      | male   |           |           |
 10111 | Chris       |             | Vizanko     | male   |           |           |
 26428 | Richard     |             | Langer      | male   |           |           |
 16240 | Jaroslav    |             | Travnicek   | male   |           |           |
 26715 | Robert      |             | Fox         | male   |           |           |
  9137 | Bruce       |             | Johnson     | male   |           |           |
 23572 | Michael     | E           | Kasinkas    | male   |           |           |
 47933 | Pat         |             | Quinn       | male   |           |           |
 17676 | John        | D           | Butler      | male   |           |           |
 11848 | David       |             | Miller      | male   |           |           |
 26012 | Rachel      | D           | Peterson    | female |           |           |
 26696 | Robert      | J           | Dietz       | male   |           |           |
 21279 | Lisa        |             | Johnson     | female |           |           |
 27886 | Scott       |             | Brown       | male   |           |           |
 26822 | Robert      |             | Nelson      | male   |           |           |
 27806 | Sarah       | J           | Peterson    | female |           |           |';