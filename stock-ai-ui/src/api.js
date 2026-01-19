import axios from "axios";

export const analyzeStock = async (symbol) => {
  const res = await axios.get(
    `http://127.0.0.1:8000/analyze/${symbol}`
  );
  return res.data;
};
