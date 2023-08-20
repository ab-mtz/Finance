# Finance
Web application to manage portafolios of stocks. Permits simulated buying and selling of stocks based on price queries (real time). Backend built with Flask. Frontend: HTML5, CSS. DB: Sqlite.

In this project, I developed a comprehensive stock trading web application that allows users to register, log in, buy and sell stocks, view their portfolio, transaction history, and even incorporate personalized features. The main aim was to create a user-friendly interface that enables users to seamlessly interact with stock data and make transactions while incorporating essential security measures.

This project allowed me to create a functional and feature-rich stock trading web application. Through the process, I gained valuable insights into web development, database management, security, and user interface design, which are essential skills in modern software development.

Project tasks description:

-Register and Login:
I implemented the registration process that requires users to provide a unique username and password. The password is securely hashed using the generate_password_hash function to enhance security. In case of errors, the application renders appropriate apologies, ensuring smooth user interaction.

-Stock Quote Lookup:
The application allows users to look up current stock prices by entering the stock's symbol. This feature employs the lookup function to fetch real-time stock data. I created templates like quote.html and quoted.html to facilitate user input and display results.

-Buying Stocks:
Users can buy stocks by entering the stock's symbol and the number of shares they wish to purchase. The application verifies the input and checks the user's available balance before completing the transaction. I utilized the lookup function to fetch the stock's current price and created necessary database tables to store purchase information.

-Selling Stocks:
The application enables users to sell stocks they own. Users select the stock symbol and input the number of shares they want to sell. Similar to the buying process, the application validates the input and ensures that the user owns the specified number of shares before completing the sale.

-View Portfolio and Transaction History:
The index route displays an HTML table summarizing the user's portfolio, including owned stocks, the number of shares, current prices, and total values. This information is fetched through multiple SELECT queries. The history route shows an HTML table with all the user's transactions, indicating whether stocks were bought or sold, the stock symbol, price, shares, and transaction date.

-Personal Touch: Password Change and Additional Cash:
I implemented a feature that allows users to change their passwords securely. Additionally, users can add extra cash to their accounts, which expands their trading capabilities. These features provide users with greater control and flexibility.

Throughout the development of this project, I gained a deeper understanding of the following concepts:

-User Authentication and Security: Implementing secure user registration and login processes was crucial. I learned about hashing passwords to protect user data and prevent unauthorized access.

-Database Management: Creating and managing database tables for user information, stock data, and transaction history required careful consideration of database design principles and appropriate use of SQLite features.

-Form Validation: Ensuring that user input is valid and error-free was essential. I learned how to validate user inputs and provide informative error messages.

-Frontend Development: Designing user interfaces using HTML and CSS, and integrating them with backend logic, helped me understand the importance of user-friendly design and smooth navigation.

-SQL Queries and Database Interaction: Writing efficient SQL queries to retrieve, insert, and update data in the database was a key skill developed during this project.
