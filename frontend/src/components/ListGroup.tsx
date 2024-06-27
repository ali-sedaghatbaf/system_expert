

function ListGroup() {
    const items = ["first", "second"];
    return <>
        <h1>List</h1>
        <ul className="list-group">
            {items.map(item => <li className="list-group-item">{item}</li>)}
        </ul>
    </>
}

export default ListGroup;