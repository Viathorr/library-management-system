import "./css/Missing.css";
import { Link } from "react-router-dom";

const Missing = () => {
    return (
        <body className="missing-container">
            <h2>Page Not Found</h2>
            <p>Well, that's disappointing.</p>
            <p>
                <Link to='/home'>Visit Our Homepage</Link>
            </p>
        </body>
    );
};

export default Missing;