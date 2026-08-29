const dotenv = require("dotenv");
const connectDB = require("./config/db");
const Temple = require("./models/Temple");

dotenv.config();

const temples = [
  {
    name: "Somnath",
    location: "Prabhas Patan",
    state: "Gujarat",
    openingTime: "06:00 AM",
    closingTime: "10:00 PM",
    description: "Major pilgrimage destination in Gujarat."
  },
  {
    name: "Dwarka",
    location: "Dwarka",
    state: "Gujarat",
    openingTime: "06:30 AM",
    closingTime: "09:30 PM",
    description: "Major pilgrimage destination in Gujarat."
  },
  {
    name: "Ambaji",
    location: "Banaskantha",
    state: "Gujarat",
    openingTime: "07:00 AM",
    closingTime: "11:30 PM",
    description: "Major pilgrimage destination in Gujarat."
  },
  {
    name: "Pavagadh",
    location: "Panchmahal",
    state: "Gujarat",
    openingTime: "06:00 AM",
    closingTime: "08:00 PM",
    description: "Major pilgrimage destination in Gujarat."
  }
];

const seedDatabase = async () => {
  try {
    await connectDB();

    await Temple.deleteMany();

    await Temple.insertMany(temples);

    console.log("Temple data inserted successfully");

    process.exit(0);
  } catch (error) {
    console.error("Seeding failed:", error.message);
    process.exit(1);
  }
};

seedDatabase();