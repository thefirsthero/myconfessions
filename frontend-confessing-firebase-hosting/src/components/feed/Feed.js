import React, { useState, useEffect } from 'react';
import Card from 'react-bootstrap/Card';
import Container from 'react-bootstrap/Container';
import axios from 'axios';
import './Feed.css';

function Feed() {
    const [confessions, setConfessions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch confessions from the API
        const baseUrl = process.env.REACT_APP_API_URL;
        const apiUrl = `${baseUrl}/`; // Replace with the correct API endpoint

        axios
            .get(apiUrl)
            .then((response) => {
                // Convert the response object to an array of confessions
                const confessionsArray = Object.values(response.data);

                // Sort the confessions by ID
                confessionsArray.sort((a, b) => parseInt(a.id) - parseInt(b.id)); // Parse ID as integers

                setConfessions(confessionsArray);
                setLoading(false);
            })
            .catch((error) => {
                console.error('Error fetching confessions', error);
                setLoading(false);
            });
    }, []);

    return (
        <div className="Feed">
            <header className="Feed-header">
                <Container>
                    <h1 className="feed-header mb-4">Confessions Feed</h1>

                    {loading && <p className="loading-message">Loading confessions...</p>}

                    {!loading && confessions.length === 0 && (
                        <p className="no-confessions-message">No confessions available.</p>
                    )}

                    {!loading && confessions.length > 0 && (
                        <div>
                            {confessions.map((confession, index) => (
                                <Card key={index} className="mb-3">
                                    <Card.Body>
                                        <Card.Title>Confession #{confession.id}</Card.Title>
                                        <Card.Text>{confession.confession}</Card.Text>
                                        <Card.Subtitle className="mb-2 text-muted">Location: {confession.location}</Card.Subtitle>
                                    </Card.Body>
                                </Card>
                            ))}
                        </div>
                    )}
                </Container>
            </header>
        </div>
    );
}

export default Feed;
