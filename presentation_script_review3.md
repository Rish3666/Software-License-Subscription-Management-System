# Review 3 — What to Say on Each Slide

Short and simple. Say it in your own words, this is just a guide.

---

**Slide 1 — Title**

Good morning everyone. My name is Rishvarma, and this is my final review for my DBMS project. The project is about managing software licenses for a whole university — which licenses we bought, who is using them, and when they expire.

---

**Slide 2 — Agenda**

Today I will cover three things. First, I will show that every requirement we promised is actually done. Second, I will demo the working system live. Third, I will walk you through the documentation and the tests.

---

**Slide 3 — Requirements Coverage**

In the first review, we listed eight things the system should do. Like recording purchases, giving licenses to users, and checking expiry. This table shows that all eight are complete, and each one points to the exact place in the code where it lives. Nothing was skipped.

---

**Slide 4 — Live Demo Walkthrough**

The demo has three parts. First I build the database from the SQL files. Then I show the day-to-day work: buying licenses, giving them to people, taking them back, and renewing them. Last, I show the reports that help the university decide what to renew and where money is being wasted.

---

**Slide 5 — Implementation: How It Was Built**

The system has three layers. At the bottom is the MySQL database with 12 tables. In the middle are the reusable views and procedures written in SQL. On top is a website built with Python Streamlit so people don't have to write queries by hand. The table on the right lists every file we shipped and what it does.

---

**Slide 6 — Implementation: Modules**

I grouped the work into five parts. Purchases, licenses, people and departments, compliance, and reports. The key point is at the bottom: all the rules sit inside the database itself, not in the website. So even if someone connects with another tool, they still cannot break the rules.

---

**Slide 7 — Application Features**

Here is what the website can do. The dashboard shows the big picture in numbers and charts. The workflow pages let you give a license to a user or take it back. The compliance page shows problems in red and can record a full check with one click.

---

**Slide 8 — Application Implementation Notes**

A few points worth mentioning. The site works with MySQL, but it also ships with a small bundled copy of the data, so it runs anywhere during a demo. When you edit a table, only the cells you actually changed get written to the database. And every form already filters its options, so you cannot even pick a license that is expired or full.

---

**Slide 9 — Screenshots (part 1)**

These are live captures from the running site. On the left is the dashboard with the expiry monitor. The middle one shows giving and taking back seats. On the right, the compliance page marks broken rules in red.

---

**Slide 10 — Screenshots (part 2)**

The first shot is the purchasing page where new buys and renewals are recorded. The second one shows the add form, where you pick a vendor from a dropdown instead of typing an ID.

---

**Slide 11 — Negative Test Evidence**

This slide answers one question: do the rules really hold when someone tries to cheat? We deliberately tried to over-allocate seats, use an expired license, put in a wrong date, and use a duplicate key. Every single attempt was rejected by the database with a clear message. That is why you can trust the numbers in the reports.

---

**Slide 12 — Documentation**

Everything is written down. The SQL scripts build the whole database from zero, in order. The README explains how to run everything and lists the rules we enforce. Anyone new can rebuild this system from these files alone.

---

**Slide 13 — Testing Summary**

Every area we tested passed. Tables get created correctly, the sample data loads, all six reports return the right numbers, and the workflows either finish completely or reverse cleanly. Reports answer in under a second at this data size.

---

**Slide 14 — Conclusion**

To wrap up: the university now has one place where every license is tracked from purchase to expiry. The rules are enforced by the database, so bad data cannot get in. As future work, I would add email alerts before licenses expire and connect it to the university login system. Thank you. Happy to take questions.
