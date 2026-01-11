#pragma once

#include <set>
#include <map>

// #include <boost/json/src.hpp>
// #include <boost/json.hpp>
#include "json/json.hpp"
#include <fstream>

using json = nlohmann::json;

class LumiFilter
{
public:
    using RunType = unsigned int;
    using LumiType = unsigned int;
    using LumiRange = std::pair<LumiType, LumiType>;
    using LumiRangeList = std::vector<LumiRange>;
    using LumiMap = std::map<RunType, LumiRangeList>;

    static json ParseFile(const std::string &jsonFile)
    {
        std::ifstream f(jsonFile);
        if (!f.is_open())
            throw std::invalid_argument("LumiFilter: Cannot open lumi json file = '" + jsonFile + "'.");
        json lumiJson = json::parse(f);

        return lumiJson;
    }

    template <typename FieldType>
    FieldType Parse(const std::string &fieldStr, const std::string &fieldName)
    {
        std::istringstream ss(fieldStr);
        FieldType field;
        ss >> field;
        if (ss.fail())
            throw std::invalid_argument("LumiFilter: Invalid " + fieldName + " = '" + fieldStr + "'.");
        return field;
    }

    LumiFilter(const std::string &lumiJsonFile)
    {
        const auto lumiJson = ParseFile(lumiJsonFile);
        if (!lumiJson.is_object())
            throw std::invalid_argument("LumiFilter: Invalid lumi json file = '" + lumiJsonFile +
                                        "'. Root element is not an object.");
        for (const auto &runStr_lumiList : lumiJson.items())
        {
            const std::string runStr = runStr_lumiList.key();
            const auto run = Parse<RunType>(runStr, "run");

            auto lumiList = runStr_lumiList.value();

            for (const auto &lumiRangeValue : lumiList)
            {
                const auto &lumiRangeArray = lumiRangeValue;
                if (lumiRangeArray.size() != 2)
                    throw std::invalid_argument("LumiFilter: Invalid lumi json file = '" + lumiJsonFile +
                                                "'. Lumi range for run = " + runStr + " has size != 2.");
                LumiRange lumiRange;
                lumiRange.first = lumiRangeArray.at(0);
                lumiRange.second = lumiRangeArray.at(1);
                lumiMap_[run].push_back(lumiRange);
            }
        }
        for (auto &[run, lumiRangeList] : lumiMap_)
        {
            if (lumiRangeList.size() > 0)
            {
                std::sort(lumiRangeList.begin(), lumiRangeList.end());
                for (size_t n = 0; n < lumiRangeList.size() - 1; ++n)
                {
                    if (lumiRangeList[n + 1].first <= lumiRangeList[n].second)
                    {
                        std::ostringstream os;
                        os << "LumiFilter: overlaping ranges for run = " << run << ". lumiRange1 = ["
                           << lumiRangeList[n].first << ", " << lumiRangeList[n].second << "]. lumiRange2 = ["
                           << lumiRangeList[n + 1].first << ", " << lumiRangeList[n + 1].second << "].";
                        throw std::invalid_argument(os.str());
                    }
                }
            }
        }
    }

    bool Pass(RunType run, LumiType luminosityBlock) const
    {
        const auto iter = lumiMap_.find(run);
        if (iter == lumiMap_.end())
            return false;
        for (const LumiRange &range : iter->second)
        {
            if (luminosityBlock < range.first)
                return false;
            if (luminosityBlock <= range.second)
                return true;
        }
        return false;
    }

private:
    LumiMap lumiMap_;
};