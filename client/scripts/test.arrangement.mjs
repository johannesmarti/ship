import { Arrangement, Position } from './arrangement.mjs'
import { Schema } from './schema.mjs'

function arraysAreEqual(arr1, arr2) {
  return arr1.length === arr2.length &&
            arr1.every((value, index) => value === arr2[index]);
}

const schema = Schema.fromJSON([
  {
    "name": "dim 1 with 3 entries",
    "indices": ["1.1", "1.2", "1.3"]
  },
  {
    "name": "dim 2 with 5 entries",
    "indices": ["2.1", "2.2", "2.3", "2.4", "2.5"]
  },
  {
    "name": "dim 3 with 2 entries",
    "indices": ["3.1", "3.2"]
  },
  {
    "name": "dim 4 with 3 entries",
    "indices": ["4.1", "4.2", "4.3"]
  },
  {
    "name": "dim 5 with 4 entries",
    "indices": ["5.1", "5.2", "5.3", "5.4"]
  }
]);

let arrangement = Arrangement.create([], [0,1,2], [3,4])

arrangement.checkAgainstSchema(schema);
console.assert(arraysAreEqual(arrangement.absoluteAddress([1, 3, 3], [7, 0]),
                              [1, 3, 3, 7, 0]),
  "absoluteAddress is reasonable");

console.assert(arrangement.isMovable(Position.row(2), Position.fixed(0)),
  "movable from row hierarchy to fixed");
console.assert(arrangement.isMovable(Position.column(1), Position.fixed(0)),
  "movable from column hierarchy to fixed");
console.assert(arrangement.isMovable(Position.column(0), Position.column(2)),
  "movable inside of column hierarchy to fixed");
console.assert(!arrangement.isMovable(Position.column(0), Position.column(1)),
  "not movable inside of column hierarchy to higher");
console.assert(!arrangement.isMovable(Position.column(0), Position.column(0)),
  "not movable inside of column hierarchy on same");

arrangement = arrangement.move(Position.column(1), Position.fixed(0), 2);
// arrangement = new Arrangement([(4,2)], [0,1,2], [3])
console.assert(arraysAreEqual(arrangement.absoluteAddress([1, 3, 3], [7]),
                              [1, 3, 3, 7, 2]),
  "absoluteAddress with fixed is reasonable");

arrangement = arrangement.move(Position.column(0), Position.row(1), 1);
// arrangement = new Arrangement([(4,2)], [0,3,1,2], [])
console.assert(arrangement.isMovable(Position.fixed(0), Position.column(0)),
  "can move fixed to empty");
console.assert(!arrangement.isMovable(Position.fixed(0), Position.row(0)),
  "can not empty fixed orders");

arrangement = arrangement.move(Position.fixed(0), Position.column(0), 2);
// arrangement = new Arrangement([], [0,3,1,2], [4])
console.assert(arrangement.isMovable(Position.column(0), Position.fixed(0)),
  "can move singleton to fixed");
console.assert(!arrangement.isMovable(Position.column(0), Position.row(0)),
  "can not empty row if fixed is empty");

arrangement = arrangement.move(Position.row(2), Position.row(1), 0);
// arrangement = new Arrangement([], [0,1,3,2], [4])
console.assert(arraysAreEqual(arrangement.absoluteAddress([1, 3, 4, 7], [0]),
                              [1, 3, 7, 4, 0]),
  "absoluteAddress after internal move is reasonable");
