BEGIN;

--https://cdn.birkie.com/Results/2011/Birkie-Skate/b_skate_overall.pdf
-- maxwell joda is listed as a female in these results, despite having a generally male name, and the
-- 9 other races were they are listed as a male
UPDATE race_result SET gender = 'male' where race_result