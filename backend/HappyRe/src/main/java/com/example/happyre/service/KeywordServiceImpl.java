package com.example.happyre.service;

import com.example.happyre.dto.keyword.KeywordEntityDTO;
import com.example.happyre.dto.message.MessageEntityDTO;
import com.example.happyre.entity.DiaryEntity;
import com.example.happyre.entity.KeywordEntity;
import com.example.happyre.entity.MessageEntity;
import com.example.happyre.entity.UserEntity;
import com.example.happyre.repository.KeywordRepository;
import io.jsonwebtoken.lang.Assert;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Transactional
@RequiredArgsConstructor
@Service
public class KeywordServiceImpl implements KeywordService {

    private final KeywordRepository keywordRepository;
    private final DiaryService diaryService;

    private static KeywordEntity getKeywordEntity(KeywordEntityDTO keywordEntityDTO, DiaryEntity diaryEntity) {
        KeywordEntity newOne = new KeywordEntity();
        newOne.setKeywordId(keywordEntityDTO.getKeywordId());
        newOne.setDiaryEntity(diaryEntity);
        newOne.setSequence(keywordEntityDTO.getSequence());
        newOne.setKeyword(keywordEntityDTO.getKeyword());
        newOne.setSummary(keywordEntityDTO.getSummary());
        newOne.setRussellX(keywordEntityDTO.getRussellX());
        newOne.setRussellY(keywordEntityDTO.getRussellY());
        return newOne;
    }

    @Override
    public KeywordEntity insert(KeywordEntity keywordEntity) {
        Assert.notNull(keywordEntity.getDiaryEntity(), "keywordEntity.diaryEntity must not be null");
        return keywordRepository.save(keywordEntity);
    }

    @Override
    public KeywordEntity insertDTO(KeywordEntityDTO keywordEntityDTO) throws Exception {
        try {
            if (this.findById(keywordEntityDTO.getKeywordId()).get() != null)
                throw new Exception("Keyword already exists");
        } catch (NullPointerException e) {

        }
        if (keywordEntityDTO.getDiaryId() == null) throw new Exception("Keyword를 등록할 Diary의 Id가 존재하지 않음");
        DiaryEntity diaryEntity = diaryService.findById(keywordEntityDTO.getDiaryId()).get();
        if (diaryEntity == null) throw new Exception("Diary does not exist");
        KeywordEntity newOne = getKeywordEntity(keywordEntityDTO, diaryEntity);
        newOne.setKeywordId(null);//insert 할 것이기 때문에 null 처리.
        return this.insert(newOne);
    }


    @Override
    public List<KeywordEntity> insertDTOList(DiaryEntity diaryEntity,List<KeywordEntityDTO> keywordEntityDTOList) {
        int cnt = 0;
        try {
            for(KeywordEntityDTO keywordEntityDTO : keywordEntityDTOList) {
                KeywordEntity keywordEntity = new KeywordEntity();
                keywordEntity.setDiaryEntity(diaryEntity);
                keywordEntity.setSequence(keywordEntityDTO.getSequence());
                keywordEntity.setKeyword(keywordEntityDTO.getKeyword());
                keywordEntity.setSummary(keywordEntityDTO.getSummary());
                keywordEntity.setRussellX(keywordEntityDTO.getRussellX());
                keywordEntity.setRussellY(keywordEntityDTO.getRussellY());

                keywordRepository.save(keywordEntity);
            }
        }catch (Exception e) {
            System.out.println("EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE");
            System.out.println(e.getMessage());
            throw new RuntimeException(e);
        }
        return null;
    }

    @Override
    public Optional<KeywordEntity> findById(int keywordId) {
        return keywordRepository.findById(keywordId);
    }

    @Override
    public List<KeywordEntity> findByDiaryEntity(DiaryEntity diaryEntity) {
        return keywordRepository.findByDiaryEntity(diaryEntity);
    }

    @Override
    public List<KeywordEntity> findByKeywordAndUserEntity(String keyword, UserEntity userEntity) {
        return keywordRepository.findByKeywordAndUserEntity(keyword, userEntity);
    }

    @Override
    public KeywordEntity update(KeywordEntity keywordDTOEntity) {
        KeywordEntity matchingEntity = keywordRepository.findById(keywordDTOEntity.getKeywordId()).orElseThrow();
        matchingEntity.setSequence(keywordDTOEntity.getSequence());
        matchingEntity.setSummary(keywordDTOEntity.getSummary());
        matchingEntity.setRussellX(keywordDTOEntity.getRussellX());
        matchingEntity.setRussellY(keywordDTOEntity.getRussellY());
        return keywordRepository.save(matchingEntity);
    }

    @Override
    public void delete(KeywordEntity keywordDTOEntity) {
        KeywordEntity matchingEntity = keywordRepository.findById(keywordDTOEntity.getKeywordId()).orElseThrow();
        keywordRepository.delete(matchingEntity);
    }
}
