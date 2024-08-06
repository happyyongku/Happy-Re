package com.example.happyre.dto.report;

import com.example.happyre.dto.diary.DiaryEntityDTO;
import com.example.happyre.dto.diaryemotion.DiaryEmotionEntityDTO;
import com.example.happyre.dto.keyword.KeywordEntityDTO;
import com.example.happyre.dto.keywordemotion.KeywordEmotionEntityDTO;
import com.example.happyre.dto.message.MessageEntityDTO;
import lombok.Data;

import java.util.List;

@Data
public class ReportDTO {
    private DiaryEntityDTO diaryEntityDTO;
    private List<MessageEntityDTO> messageEntityDTOList;
    private List<KeywordEntityDTO> keywordEntityDTOList;
    private List<DiaryEmotionEntityDTO> diaryEmotionEntityDTOList;
    private List<KeywordEmotionEntityDTO> keywordEmotionEntityDTOList;
}